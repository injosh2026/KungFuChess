from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.position import Position

from .sliding_rule import SlidingRule


class RookRule:
    """
    Defines movement rules for rook pieces.

    A rook can move any number of squares horizontally
    or vertically until blocked by another piece.
    """

    DIRECTIONS = (
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
    )

    def legal_destinations(self, board: Board, piece: Piece) -> set[Position]:
        """
        Calculates all legal destinations for a rook.

        Args:
            board: Current game board.
            piece: Rook piece to evaluate.

        Returns:
            Set of positions reachable by the rook.
        """
        return SlidingRule.calculate_destinations(board, piece, self.DIRECTIONS)
