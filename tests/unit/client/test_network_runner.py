import asyncio

from kungfu_chess.client.network_runner import NetworkRunner


class FakeClient:

    def __init__(self):
        self.started = False

    async def start(self):
        self.started = True


class FakeGameApp:

    def __init__(self):
        self.ran = False

    def run(self):
        self.ran = True


def test_network_runner_starts_client_and_runs_game_app():

    client = FakeClient()
    game_app = FakeGameApp()

    runner = NetworkRunner(
        client,
        game_app,
    )

    asyncio.run(
        runner.run()
    )

    assert client.started is True
    assert game_app.ran is True

