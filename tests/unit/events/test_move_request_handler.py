from kungfu_chess.events.handlers.move_request_handler import (
    MoveRequestHandler,
)
from kungfu_chess.events.messages.move_requested_message import (
    MoveRequestedMessage,
)
from kungfu_chess.model.position import Position


class FakeGameEngine:

    def __init__(self):
        self.calls = []

    def request_move(self, source, destination):
        self.calls.append(
            (source, destination)
        )

        return "move_result"


def test_handler_forwards_message_to_engine():

    engine = FakeGameEngine()

    handler = MoveRequestHandler(engine)

    message = MoveRequestedMessage(
        source=Position(0, 0),
        destination=Position(0, 1),
    )

    result = handler.handle(message)

    assert result == "move_result"

    assert engine.calls == [
        (
            Position(0, 0),
            Position(0, 1),
        )
    ]