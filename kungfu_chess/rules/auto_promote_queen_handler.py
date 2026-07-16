from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.rules.pawn_end_outcome import PawnEndOutcome


class AutoPromoteQueenHandler:
    """
    Promotes a pawn automatically to a queen on the last rank.

    This handler supports chess-style auto promotion only.
    """

    WHITE_PROMOTION_RANK = 0
    BLACK_PROMOTION_RANK = 7

    def resolve(
        self,
        piece: Piece,
        landing_cell: Position,
        board: Board,
    ) -> PawnEndOutcome:
        if piece.kind != PieceKind.PAWN:
            return PawnEndOutcome()

        if piece.color == Color.WHITE:
            if landing_cell.row == self.WHITE_PROMOTION_RANK:
                return PawnEndOutcome(new_kind=PieceKind.QUEEN)
            return PawnEndOutcome()

        if landing_cell.row == self.BLACK_PROMOTION_RANK:
            return PawnEndOutcome(new_kind=PieceKind.QUEEN)

        return PawnEndOutcome()
