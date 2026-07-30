import json

from kungfu_chess.events.motion_started_event import MotionStartedEvent
from kungfu_chess.model.position import Position


class MotionStartedSerializer:

    @staticmethod
    def serialize(event: MotionStartedEvent) -> str:
        return json.dumps(MotionStartedSerializer.to_dict(event))

    @staticmethod
    def to_dict(event: MotionStartedEvent) -> dict:
        return {
            "type": "MOTION_STARTED",
            "payload": {
                "piece_id": event.piece_id,
                "start": MotionStartedSerializer._serialize_position(event.start),
                "target": MotionStartedSerializer._serialize_position(event.target),
                "duration_ms": event.duration_ms,
                "state": event.state,
                "timestamp_ms": event.timestamp_ms,
            },
        }

    @staticmethod
    def deserialize(message: str) -> MotionStartedEvent | None:
        if not isinstance(message, str):
            return None

        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            return None

        if data.get("type") != "MOTION_STARTED":
            return None

        payload = data["payload"]

        return MotionStartedEvent(
            timestamp_ms=payload["timestamp_ms"],
            piece_id=payload["piece_id"],
            start=MotionStartedSerializer._deserialize_position(payload["start"]),
            target=MotionStartedSerializer._deserialize_position(payload["target"]),
            duration_ms=payload["duration_ms"],
            state=payload["state"],
        )

    @staticmethod
    def _serialize_position(position: Position) -> dict:
        return {
            "row": position.row,
            "col": position.col,
        }

    @staticmethod
    def _deserialize_position(data: dict) -> Position:
        return Position(
            row=data["row"],
            col=data["col"],
        )
