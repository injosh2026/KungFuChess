from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.position import Position

from .sliding_rule import SlidingRule


class QueenRule:

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

    def legal_destinations(
        self,
        board: Board,
        piece: Piece
    ) -> set[Position]:

        return SlidingRule.calculate_destinations(
            board,
            piece,
            self.DIRECTIONS
        )