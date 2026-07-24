from kungfu_chess.network.local_transport import LocalConnection
from kungfu_chess.server.game_server import GameServer
from tests.unit.server.test_game_server import DummyGameSession


def test_game_server_uses_client_connection():

    server = GameServer()

    server.create_match(
        "match1",
        DummyGameSession(),
    )

    client_connection = LocalConnection()
    server_connection = LocalConnection()

    client_connection.connect_to(server_connection)
    server_connection.connect_to(client_connection)

    session = server.join_match(
        "match1",
        "player1",
        server_connection,
    )

    message = object()

    session.send(message)

    assert client_connection.receive() == message
