class Client:

    def __init__(
        self,
        session,
    ):
        self.session = session
        self.messages = []

    async def listen(self):

        while True:
            message = await self.session.receive()

            print(
                "Received:",
                message,
            )

    async def listen_once(self):

        message = await self.session.receive()

        self.messages.append(message)

    async def start(self):

        await self.listen()

    async def send(self, message):
        await self.session.send(message)