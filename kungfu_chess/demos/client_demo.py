import asyncio
import sys

from img import Img

from kungfu_chess.network.websocket_client import WebSocketClient
from kungfu_chess.ui.network_composition_root import build_network_runner


async def main():

    player_id = sys.argv[1]

    websocket_client = WebSocketClient()

    await websocket_client.connect()

    connection = websocket_client

    await connection.send(
        f"JOIN {player_id}",
    )

    runner = build_network_runner(
        Img(),
        connection,
    )

    await runner.run()


if __name__ == "__main__":
    asyncio.run(main())