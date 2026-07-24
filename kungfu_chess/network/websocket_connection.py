import asyncio


class WebSocketConnection:

    def __init__(self, websocket):
        self.websocket = websocket
        self.loop = asyncio.get_running_loop()

    def send(self, message):
        asyncio.create_task(self.websocket.send(str(message)))

    async def receive(self):
        return await self.websocket.recv()
