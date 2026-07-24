class ClientSession:

    def __init__(
        self,
        player_id,
        connection,
    ):
        self.player_id = player_id
        self.connection = connection


    async def send(self, message):
        await self.connection.send(message)


    async def receive(self):
        return await self.connection.receive()