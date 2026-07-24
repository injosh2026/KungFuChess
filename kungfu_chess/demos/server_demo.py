import asyncio

from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.io.board_parser import BoardParser
from kungfu_chess.network.websocket_server import WebSocketServer
from kungfu_chess.server.game_server import GameServer


async def game_loop(game_session):

    while True:
        game_session.game_engine.wait(16)

        await asyncio.sleep(0.016)

async def main():

    board = BoardParser().parse(
        [
            "wR .",
            ". bK",
        ]
    )

    game_session = GameFactory.create_session(board)

    asyncio.create_task(
        game_loop(game_session)
    )

    game_server = GameServer()

    game_server.create_match(
        "match1",
        game_session,
    )

    websocket_server = WebSocketServer(game_server)

    await websocket_server.start()

    print("Server started")
    print("Waiting for players...")

    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
