import inspect
import json
from collections.abc import Callable

from kungfu_chess.events.motion_started_event import MotionStartedEvent
from kungfu_chess.network.motion_started_serializer import MotionStartedSerializer
from kungfu_chess.network.snapshot_deserializer import SnapshotDeserializer


class ClientSession:

    def __init__(
        self,
        player_id,
        connection,
        snapshot_source,
        on_motion_started: Callable[[MotionStartedEvent], None] | None = None,
    ):
        self.player_id = player_id
        self.connection = connection
        self.snapshot_source = snapshot_source
        self._on_motion_started = on_motion_started
        self.events = []

    async def send(self, message):
        await self.connection.send(message)

    async def receive(self):

        result = self.connection.receive()

        if inspect.isawaitable(result):
            message = await result
        else:
            message = result

        print("RAW MESSAGE:", message)

        message_type = self._message_type(message)

        if message_type == "GAME_SNAPSHOT":
            snapshot = SnapshotDeserializer.deserialize(message)

            print("DESERIALIZED:", snapshot)

            if snapshot is not None:
                self.snapshot_source.update(snapshot)
        elif message_type == "MOTION_STARTED" and self._on_motion_started is not None:
            event = MotionStartedSerializer.deserialize(message)

            print("DESERIALIZED:", event)

            if event is not None:
                self._on_motion_started(event)

        self.events.append(message)

        return message

    @staticmethod
    def _message_type(message) -> str | None:
        if not isinstance(message, str):
            return None

        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            return None

        message_type = data.get("type")
        if not isinstance(message_type, str):
            return None

        return message_type
