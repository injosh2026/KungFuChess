import asyncio
import sys

from kungfu_chess.network.websocket_client import WebSocketClient


async def main():

    player_id = sys.argv[1]

    client = WebSocketClient()

    await client.connect()

    print(
        "Connected as",
        player_id,
    )

    await client.send(f"JOIN {player_id}")

    print("Sending move")

    await client.send("MOVE 0 0 0 1")

    while True:

        message = await client.receive()

        print(
            "Received:",
            message,
        )


if __name__ == "__main__":
    asyncio.run(main())
