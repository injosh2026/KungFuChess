from typing import Protocol

from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.position import Position
from kungfu_chess.rules.pawn_end_outcome import PawnEndOutcome


class PawnEndHandler(Protocol):
    """
    Decides what happens when a piece completes a move on a landing cell.

    Implementations are stateless and return decisions only.
    """

    def resolve(
        self,
        piece: Piece,
        landing_cell: Position,
        board: Board,
    ) -> PawnEndOutcome:
        """
        Inspects a completed landing and returns any rank-end action.
        """
