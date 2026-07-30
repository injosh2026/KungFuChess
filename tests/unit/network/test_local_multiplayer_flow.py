import json

from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.events.messages.move_requested_message import MoveRequestedMessage
from kungfu_chess.io.board_parser import BoardParser
from kungfu_chess.model.position import Position
from kungfu_chess.network.local_transport import LocalConnection
from kungfu_chess.server.game_server import GameServer


def test_local_client_server_snapshot_flow():

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

    player = server.join_match(
        "match1",
        "white",
        server_connection,
    )

    player.receive(
        MoveRequestedMessage(
            source=Position(0, 0),
            destination=Position(0, 1),
        )
    )

    game_session.game_engine.wait(2500)

    motion_message = json.loads(client_connection.receive())
    assert motion_message["type"] == "MOTION_STARTED"

    message = client_connection.receive()

    data = json.loads(message)

    assert data["type"] == "GAME_SNAPSHOT"

    pieces = data["payload"]["pieces"]

    rook = next(
        piece
        for piece in pieces
        if piece["kind"] == "ROOK"
        and piece["color"] == "WHITE"
    )

    assert rook["position"]["row"] == 0
    assert rook["position"]["col"] == 1