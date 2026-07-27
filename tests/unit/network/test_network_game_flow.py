import asyncio

from kungfu_chess.client.client import Client
from kungfu_chess.client.client_session import ClientSession
from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.events.messages.move_requested_message import MoveRequestedMessage
from kungfu_chess.io.board_parser import BoardParser
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.network.local_transport import LocalConnection
from kungfu_chess.network.snapshot_serializer import SnapshotSerializer
from kungfu_chess.snapshot.network_snapshot_source import NetworkSnapshotSource
from kungfu_chess.server.game_server import GameServer


def test_client_server_snapshot_flow_updates_game_view():

    board = BoardParser().parse(
        [
            "wR .",
            ". bK",
        ]
    )

    game_session = GameFactory.create_session(board)

    server = GameServer()

    server.create_match(
        "match1",
        game_session,
    )

    client_connection = LocalConnection()
    server_connection = LocalConnection()

    client_connection.connect_to(server_connection)
    server_connection.connect_to(client_connection)

    server.join_match(
        "match1",
        "white",
        server_connection,
    )

    snapshot_source = NetworkSnapshotSource(
        client_connection,
    )

    client_session = ClientSession(
        "white",
        client_connection,
        snapshot_source,
    )

    client = Client(client_session)

    snapshot = game_session.snapshot_builder.build(
        game_session.game_engine.game_state,
    )

    server_connection.send(SnapshotSerializer.serialize(snapshot))

    asyncio.run(client.listen_once())

    snapshot = snapshot_source.get_snapshot()

    assert snapshot is not None

    rook = next(
        piece
        for piece in snapshot.pieces
        if piece.kind == PieceKind.ROOK and piece.color == Color.WHITE
    )

    assert rook.position == Position(0, 0)
