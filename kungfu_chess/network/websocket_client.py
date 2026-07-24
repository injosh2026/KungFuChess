import websockets


class WebSocketClient:

    def __init__(
        self,
        uri="ws://localhost:8765",
    ):
        self.uri = uri
        self.websocket = None


    async def connect(self):

        self.websocket = await websockets.connect(
            self.uri
        )


    async def send(self, message):

        await self.websocket.send(message)


    async def receive(self):

        return await self.websocket.recv()