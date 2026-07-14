from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.position import Position

from .sliding_rule import SlidingRule


class QueenRule:
    """
    Defines movement rules for queen pieces.

    A queen combines rook-like and bishop-like movement,
    allowing movement along rows, columns, and diagonals.
    """

    DIRECTIONS = (
        # Rook directions
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
        # Bishop directions
        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1),
    )

    def legal_destinations(self, board: Board, piece: Piece) -> set[Position]:
        """
        Calculates all legal destinations for a queen.

        Args:
            board: Current game board.
            piece: Queen piece to evaluate.

        Returns:
            Positions reachable by the queen.
        """
        return SlidingRule.calculate_destinations(board, piece, self.DIRECTIONS)
