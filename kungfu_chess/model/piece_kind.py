from enum import Enum


class PieceKind(Enum):
    """
    Identifies the type of a chess piece.

    The enum defines piece categories only. Movement rules,
    rendering, scoring, and other behaviors are implemented
    by separate components.
    """

    KING = "king"
    QUEEN = "queen"
    ROOK = "rook"
    BISHOP = "bishop"
    KNIGHT = "knight"
    PAWN = "pawn"
