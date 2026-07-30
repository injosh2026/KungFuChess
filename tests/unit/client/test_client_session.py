import asyncio
import json

from kungfu_chess.client.client_session import ClientSession
from kungfu_chess.events.motion_started_event import MotionStartedEvent
from kungfu_chess.model.position import Position
from kungfu_chess.network.motion_started_serializer import MotionStartedSerializer
from kungfu_chess.network.snapshot_serializer import SnapshotSerializer
from kungfu_chess.snapshot.game_snapshot import GameSnapshot
from kungfu_chess.snapshot.network_snapshot_source import NetworkSnapshotSource


class DummyConnection:

    def __init__(self, message="EVENT"):
        self.messages = []
        self._message = message

    async def receive(self):
        return self._message

    def receive_sync(self):
        return self._message

    async def send(self, message):
        self.messages.append(message)


class RecordingSnapshotSource:

    def __init__(self):
        self.updates = []

    def update(self, snapshot):
        self.updates.append(snapshot)


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


def test_client_session_game_snapshot_updates_snapshot_source():
    snapshot = GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=[],
        selected_cell=None,
        legal_moves=set(),
        game_over=False,
    )
    wire_message = SnapshotSerializer.serialize(snapshot)

    connection = DummyConnection(wire_message)
    snapshot_source = RecordingSnapshotSource()

    session = ClientSession(
        "player1",
        connection,
        snapshot_source,
    )

    asyncio.run(session.receive())

    assert snapshot_source.updates == [snapshot]


def test_client_session_motion_started_invokes_callback():
    event = MotionStartedEvent(
        timestamp_ms=0,
        piece_id=1,
        start=Position(0, 0),
        target=Position(0, 1),
        duration_ms=1000,
        state="move",
    )
    wire_message = MotionStartedSerializer.serialize(event)

    connection = DummyConnection(wire_message)
    received_events = []

    session = ClientSession(
        "player1",
        connection,
        RecordingSnapshotSource(),
        on_motion_started=received_events.append,
    )

    asyncio.run(session.receive())

    assert received_events == [event]
    assert json.loads(session.events[0])["type"] == "MOTION_STARTED"
