import json

from kungfu_chess.events.motion_started_event import MotionStartedEvent
from kungfu_chess.model.position import Position
from kungfu_chess.network.motion_started_serializer import MotionStartedSerializer


def test_motion_started_serializer_round_trip():
    event = MotionStartedEvent(
        timestamp_ms=250,
        piece_id=3,
        start=Position(1, 2),
        target=Position(4, 5),
        duration_ms=1200,
        state="move",
    )

    wire = MotionStartedSerializer.serialize(event)
    restored = MotionStartedSerializer.deserialize(wire)

    assert restored == event

    data = json.loads(wire)
    payload = data["payload"]

    assert data["type"] == "MOTION_STARTED"
    assert payload["piece_id"] == 3
    assert payload["start"] == {"row": 1, "col": 2}
    assert payload["target"] == {"row": 4, "col": 5}
    assert payload["duration_ms"] == 1200
    assert payload["state"] == "move"
    assert payload["timestamp_ms"] == 250
