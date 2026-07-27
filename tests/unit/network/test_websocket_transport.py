import asyncio

from kungfu_chess.network.websocket_server import WebSocketServer
from kungfu_chess.network.websocket_client import WebSocketClient
from kungfu_chess.server.game_server import GameServer


def test_websocket_client_receives_broadcast():

    async def run():
        game_server = GameServer()

        server = WebSocketServer(game_server)

        await server.start()

        try:
            client1 = WebSocketClient()
            client2 = WebSocketClient()

            await client1.connect()
            await client2.connect()

            await client1.send("hello")

            message = await client2.receive()

            assert message == "hello"

        finally:
            await server.stop()

    asyncio.run(run())
