import asyncio

from kungfu_chess.network.connection import Connection


class WebSocketConnection(Connection):

    def __init__(self, websocket):
        self.websocket = websocket
        self.loop = asyncio.get_running_loop()

    def send(self, message) -> None:
        asyncio.run_coroutine_threadsafe(
            self.websocket.send(str(message)),
            self.loop,
        )

    async def receive(self):
        return await self.websocket.recv()
