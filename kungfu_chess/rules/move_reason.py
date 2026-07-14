from enum import Enum


class MoveReason(Enum):
    """
    Reasons describing the result of move validation.

    These values are used by the rule engine to explain
    why a requested movement was accepted or rejected.
    """
    OK = "ok"
    OUTSIDE_BOARD = "outside_board"
    EMPTY_SOURCE = "empty_source"
    FRIENDLY_DESTINATION = "friendly_destination"
    ILLEGAL_PIECE_MOVE = "illegal_piece_move"
    UNKNOWN_PIECE_RULE = "unknown_piece_rule"
