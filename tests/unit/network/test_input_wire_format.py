import pytest

from kungfu_chess.events.messages.jump_requested_message import JumpRequestedMessage
from kungfu_chess.events.messages.move_requested_message import MoveRequestedMessage
from kungfu_chess.events.messages.promotion_requested_message import (
    PromotionRequestedMessage,
)
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position


def test_move_requested_message_wire_format_round_trip():
    message = MoveRequestedMessage(
        source=Position(0, 1),
        destination=Position(2, 3),
    )

    wire = message.to_wire_format()

    assert wire == "MOVE 0 1 2 3"
    assert MoveRequestedMessage.from_wire_format(wire) == message


def test_move_requested_message_from_wire_format_rejects_invalid_text():
    with pytest.raises(ValueError):
        MoveRequestedMessage.from_wire_format("JUMP 1")


def test_jump_requested_message_wire_format_round_trip():
    message = JumpRequestedMessage(piece_id=7)

    wire = message.to_wire_format()

    assert wire == "JUMP 7"
    assert JumpRequestedMessage.from_wire_format(wire) == message


def test_jump_requested_message_from_wire_format_rejects_invalid_text():
    with pytest.raises(ValueError):
        JumpRequestedMessage.from_wire_format("MOVE 0 0 1 1")


def test_promotion_requested_message_wire_format_round_trip():
    message = PromotionRequestedMessage(
        piece_id=4,
        chosen_kind=PieceKind.QUEEN,
    )

    wire = message.to_wire_format()

    assert wire == "PROMOTION 4 QUEEN"
    assert PromotionRequestedMessage.from_wire_format(wire) == message


def test_promotion_requested_message_from_wire_format_rejects_invalid_text():
    with pytest.raises(ValueError):
        PromotionRequestedMessage.from_wire_format("PROMOTION 4 INVALID")
