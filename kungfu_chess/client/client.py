class Client:

    def __init__(
        self,
        session,
    ):
        self.session = session


    async def listen(self):

        while True:
            message = await self.session.receive()

            print(
                "Received:",
                message,
            )