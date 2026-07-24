from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.io.board_parser import BoardParser
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

    print("Server running")
    print("Waiting for players...")


if __name__ == "__main__":
    main()