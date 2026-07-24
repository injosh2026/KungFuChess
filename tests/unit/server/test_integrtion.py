from kungfu_chess.config.piece_code import piece_code
from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.events.messages.move_requested_message import MoveRequestedMessage
from kungfu_chess.io.board_parser import BoardParser
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.network.local_transport import LocalConnection
from kungfu_chess.server.game_server import GameServer


def test_two_players_receive_same_move_event():
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

    white_client_connection = LocalConnection()
    white_server_connection = LocalConnection()

    white_client_connection.connect_to(white_server_connection)

    white_server_connection.connect_to(white_client_connection)

    black_client_connection = LocalConnection()
    black_server_connection = LocalConnection()

    black_client_connection.connect_to(black_server_connection)

    black_server_connection.connect_to(black_client_connection)

    white = server.join_match(
        "match1",
        "white",
        white_server_connection,
    )

    black = server.join_match(
        "match1",
        "black",
        black_server_connection,
    )

    white.receive(
        MoveRequestedMessage(
            source=Position(0, 0),
            destination=Position(0, 1),
        )
    )

    game_session.game_engine.wait(2500)

    white_message = white_client_connection.receive()
    black_message = black_client_connection.receive()

    assert white_message == black_message

    event = white_message

    assert event.from_position == Position(0, 0)
    assert event.to_position == Position(0, 1)
    assert event.piece_code == piece_code(
        PieceKind.ROOK,
        Color.WHITE,
    )
