from kungfu_chess.events.message_bus import MessageBus
from kungfu_chess.network.local_transport import LocalConnection
from kungfu_chess.server.game_server import GameServer
from kungfu_chess.server.player_color import PlayerColor
from kungfu_chess.server.server_session import ServerSession


class DummyGameSession:
    def __init__(self):
        self.message_bus = MessageBus()


def test_game_server_creates_match():

    server = GameServer()

    match = server.create_match(
        "match1",
        DummyGameSession(),
    )

    assert server.matches["match1"] is match


def test_game_server_player_joins_match():

    server = GameServer()

    server.create_match(
        "match1",
        DummyGameSession(),
    )

    connection = LocalConnection()

    session = server.join_match(
        "match1",
        "player1",
        connection,
    )

    assert session.player_id == "player1"


def test_game_server_stores_connected_players():

    server = GameServer()

    server.create_match(
        "match1",
        DummyGameSession(),
    )

    connection = LocalConnection()

    server.join_match(
        "match1",
        "player1",
        connection,
    )

    assert "player1" in server.sessions


from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.io.board_parser import BoardParser


def test_game_server_accepts_real_game_session():

    parser = BoardParser()

    board = parser.parse(
        [
            "wK .",
            ". bK",
        ]
    )

    game_session = GameFactory.create_session(board)

    server = GameServer()

    match = server.create_match(
        "match1",
        game_session,
    )

    assert match.game_session is game_session
    assert match.game_session.game_engine is not None
    assert match.game_session.message_bus is not None


def test_game_server_assigns_player_color_to_session():

    server = GameServer()

    connection = LocalConnection()

    server.create_match(
        "match1",
        DummyGameSession(),
    )

    session = server.join_match(
        "match1",
        "player1",
        connection,
    )

    assert session.color == PlayerColor.WHITE


def test_second_player_gets_black():

    server = GameServer()

    connection = LocalConnection()

    server.create_match(
        "match1",
        DummyGameSession(),
    )

    server.join_match(
        "match1",
        "player1",
        connection,
    )

    session = server.join_match(
        "match1",
        "player2",
        connection,
    )

    assert session.color == PlayerColor.BLACK
