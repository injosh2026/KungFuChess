from enum import Enum


class MoveReason(Enum):
    OK = "ok"
    OUTSIDE_BOARD = "outside_board"
    EMPTY_SOURCE = "empty_source"
    FRIENDLY_DESTINATION = "friendly_destination"
    ILLEGAL_PIECE_MOVE = "illegal_piece_move"
