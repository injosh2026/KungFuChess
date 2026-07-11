from enum import Enum


class PieceState(Enum):
    IDLE = "idle"
    MOVING = "moving"
    CAPTURED = "captured"
