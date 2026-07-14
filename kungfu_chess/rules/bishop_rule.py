from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.position import Position

from .sliding_rule import SlidingRule


class BishopRule:
    """
    Defines movement rules for bishop-like pieces.

    A bishop moves diagonally any number of cells
    until reaching the board boundary or another piece.

    This class calculates legal destinations only.
    It does not move pieces or modify game state.
    """

    DIRECTIONS = (
        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1),
    )

    def legal_destinations(self, board: Board, piece: Piece) -> set[Position]:
        """
        Returns all legal destination positions for the piece.

        Args:
            board: Current board state.
            piece: Piece whose movement is being evaluated.

        Returns:
            Set of positions reachable by diagonal movement.
        """
        return SlidingRule.calculate_destinations(board, piece, self.DIRECTIONS)
