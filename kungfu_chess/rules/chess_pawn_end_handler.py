from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.rules.pawn_end_outcome import PawnEndOutcome


class ChessPawnEndHandler:
    """
    Returns a deferred promotion choice when a pawn reaches the last rank.

    Chess mode lets the player choose among queen, rook, bishop, or knight.
    """

    WHITE_PROMOTION_RANK = 0
    BLACK_PROMOTION_RANK = 7

    PROMOTION_KINDS = frozenset(
        {
            PieceKind.QUEEN,
            PieceKind.ROOK,
            PieceKind.BISHOP,
            PieceKind.KNIGHT,
        }
    )

    def resolve(
        self,
        piece: Piece,
        landing_cell: Position,
        board: Board,
    ) -> PawnEndOutcome:
        if piece.kind != PieceKind.PAWN:
            return PawnEndOutcome.no_action()

        if piece.color == Color.WHITE:
            if landing_cell.row == self.WHITE_PROMOTION_RANK:
                return PawnEndOutcome.pending_choice(self.PROMOTION_KINDS)
            return PawnEndOutcome.no_action()

        if landing_cell.row == self.BLACK_PROMOTION_RANK:
            return PawnEndOutcome.pending_choice(self.PROMOTION_KINDS)

        return PawnEndOutcome.no_action()
