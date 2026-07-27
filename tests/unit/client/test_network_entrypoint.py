import asyncio

from kungfu_chess.client.network_entrypoint import start_network_game


class FakeRunner:

    def __init__(self):
        self.started = False

    async def run(self):
        self.started = True


def test_network_entrypoint_starts_runner(monkeypatch):

    runner = FakeRunner()

    def fake_build_network_runner(
        image,
        connection,
    ):
        return runner

    monkeypatch.setattr(
        "kungfu_chess.client.network_entrypoint.build_network_runner",
        fake_build_network_runner,
    )

    asyncio.run(
        start_network_game(
            object(),
            object(),
        )
    )

    assert runner.started is True