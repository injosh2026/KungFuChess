import asyncio

from kungfu_chess.client.client_session import ClientSession
from kungfu_chess.snapshot.network_snapshot_source import NetworkSnapshotSource


class DummyConnection:

    def __init__(self):
        self.messages = []

    async def receive(self):
        return "EVENT"

    async def send(self, message):
        self.messages.append(message)


def test_client_session_stores_received_event():

    connection = DummyConnection()

    session = ClientSession(
        "player1",
        connection,
        NetworkSnapshotSource(connection),
    )

    message = asyncio.run(session.receive())

    assert message == "EVENT"
    assert session.events == ["EVENT"]
