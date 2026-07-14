from enum import Enum


class PieceState(Enum):
    """
    Represents the lifecycle state of a game piece.

    The state describes whether a piece is currently idle,
    moving, or has been captured. Movement details such as
    destination and elapsed time are stored separately in Motion.
    """

    IDLE = "idle"
    MOVING = "moving"
    CAPTURED = "captured"
