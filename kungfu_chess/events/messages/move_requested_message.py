from dataclasses import dataclass

from kungfu_chess.model.position import Position


@dataclass(frozen=True, slots=True)
class MoveRequestedMessage:
    """
    Request to move a piece from one position to another.

    This message represents an intention to move.
    It does not perform validation and does not modify game state.

    The receiver decides whether the requested move is allowed.
    """

    source: Position
    destination: Position