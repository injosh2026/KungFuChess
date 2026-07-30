import asyncio
from types import SimpleNamespace

from kungfu_chess.client.client_session import ClientSession
from kungfu_chess.client.connection_command_sender import ConnectionCommandSender
from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.events.handlers.jump_request_handler import JumpRequestHandler
from kungfu_chess.events.handlers.move_request_handler import MoveRequestHandler
from kungfu_chess.events.handlers.promotion_request_handler import (
    PromotionRequestHandler,
)
from kungfu_chess.events.message_bus import MessageBus
from kungfu_chess.events.messages.jump_requested_message import JumpRequestedMessage
from kungfu_chess.events.messages.move_requested_message import MoveRequestedMessage
from kungfu_chess.events.messages.promotion_requested_message import (
    PromotionRequestedMessage,
)
from kungfu_chess.input.board_mapper import BoardMapper
from kungfu_chess.input.controller import Controller
from kungfu_chess.io.board_parser import BoardParser
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.network.local_transport import LocalConnection
from kungfu_chess.network.websocket_server import WebSocketServer
from kungfu_chess.snapshot.network_snapshot_source import NetworkSnapshotSource
from kungfu_chess.server.game_server import GameServer

CELL_SIZE = GameFactory.CELL_SIZE


def _build_client_input_stack(connection):
    board_parser = BoardParser()
    board = board_parser.parse(
        [
            "wR .",
            ". bK",
        ]
    )
    board_mapper = BoardMapper(CELL_SIZE)
    message_bus = MessageBus()
    command_sender = ConnectionCommandSender(connection)

    message_bus.subscribe(
        MoveRequestedMessage,
        MoveRequestHandler(command_sender).handle,
    )
    message_bus.subscribe(
        JumpRequestedMessage,
        JumpRequestHandler(command_sender).handle,
    )
    message_bus.subscribe(
        PromotionRequestedMessage,
        PromotionRequestHandler(command_sender).handle,
    )

    game_queries = SimpleNamespace(
        is_piece_in_cooldown=lambda piece_id: False,
        get_legal_moves=lambda position: set(),
    )

    controller = Controller(
        board,
        board_mapper,
        game_queries,
        message_bus,
    )

    snapshot_source = NetworkSnapshotSource(connection, controller=controller)
    client_session = ClientSession("white", connection, snapshot_source)

    def sync_controller_board_from_snapshot() -> None:
        snapshot = snapshot_source.get_snapshot()
        if snapshot is not None:
            controller.board = board_parser.from_snapshot(snapshot)

    return controller, snapshot_source, client_session, sync_controller_board_from_snapshot


def _forward_pending_input(server_connection, server_session) -> None:
    while True:
        wire_message = server_connection.receive()
        if wire_message is None:
            return

        domain_message = WebSocketServer._parse_input_command(wire_message)
        if domain_message is not None:
            server_session.receive(domain_message)


def test_client_click_flow_updates_snapshot_from_server():
    board = BoardParser().parse(
        [
            "wR .",
            ". bK",
        ]
    )

    game_session = GameFactory.create_session(board)
    server = GameServer()
    server.create_match("match1", game_session)

    client_connection = LocalConnection()
    server_connection = LocalConnection()
    client_connection.connect_to(server_connection)
    server_connection.connect_to(client_connection)

    server_session = server.join_match(
        "match1",
        "white",
        server_connection,
    )

    controller, snapshot_source, client_session, sync_board = _build_client_input_stack(
        client_connection,
    )

    server_session.send_initial_snapshot()
    asyncio.run(client_session.receive())

    sync_board()
    controller.handle_click(CELL_SIZE // 2, CELL_SIZE // 2)

    sync_board()
    controller.handle_click(CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2)

    _forward_pending_input(server_connection, server_session)

    game_session.game_engine.wait(2500)

    asyncio.run(client_session.receive())
    asyncio.run(client_session.receive())

    snapshot = snapshot_source.get_snapshot()

    assert snapshot is not None

    rook = next(
        piece
        for piece in snapshot.pieces
        if piece.kind == PieceKind.ROOK and piece.color == Color.WHITE
    )

    assert rook.position == Position(0, 1)
