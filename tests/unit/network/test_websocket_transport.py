import asyncio

from kungfu_chess.network.websocket_server import WebSocketServer
from kungfu_chess.network.websocket_client import WebSocketClient


def test_websocket_client_receives_broadcast():

    async def run():

        server = WebSocketServer()

        await server.start()

        client1 = WebSocketClient()
        client2 = WebSocketClient()

        await client1.connect()
        await client2.connect()

        await client1.send(
            "hello"
        )

        message = await client2.receive()

        assert message == "hello"


    asyncio.run(run())