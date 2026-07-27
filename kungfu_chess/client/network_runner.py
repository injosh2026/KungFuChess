import asyncio


class NetworkRunner:

    def __init__(
        self,
        client,
        game_app,
    ):
        self._client = client
        self._game_app = game_app


    async def run(self):

        asyncio.create_task(
            self._client.start(),
        )

        loop = asyncio.get_running_loop()

        await loop.run_in_executor(
            None,
            self._game_app.run,
        )