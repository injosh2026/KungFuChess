from multiprocessing.connection import Client

from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.events.messages.move_requested_message import MoveRequestedMessage
from kungfu_chess.io.board_parser import BoardParser
from kungfu_chess.model.position import Position
from kungfu_chess.network.local_transport import LocalConnection
from kungfu_chess.server.game_server import GameServer


def main():

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

    white_connection = LocalConnection()
    white_server_connection = LocalConnection()

    white_connection.connect_to(white_server_connection)

    white_server_connection.connect_to(white_connection)

    white_client = Client(white_connection)

    white = server.join_match(
        "match1",
        "player1",
        white_server_connection,
    )

    black_connection = LocalConnection()
    black_server_connection = LocalConnection()

    black_connection.connect_to(black_server_connection)

    black_server_connection.connect_to(black_connection)

    black_client = Client(black_connection)

    black = server.join_match(
        "match1",
        "player2",
        black_server_connection
    )

    print("Server running")
    print("White connected:", white.player_id)
    print("Black connected:", black.player_id)

    white.receive(
        MoveRequestedMessage(
            source=Position(0, 0),
            destination=Position(0, 1),
        )
    )

    game_session.game_engine.wait(2500)

    print(white.outbox)
    print(black.outbox)


if __name__ == "__main__":
    main()
