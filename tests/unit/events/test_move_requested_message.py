from kungfu_chess.events.messages.move_requested_message import (
    MoveRequestedMessage,
)
from kungfu_chess.model.position import Position


def test_move_requested_message_contains_move_data():

    message = MoveRequestedMessage(
        source=Position(0, 0),
        destination=Position(0, 1),
    )

    assert message.source == Position(0, 0)
    assert message.destination == Position(0, 1)