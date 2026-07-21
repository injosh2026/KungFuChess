from dataclasses import dataclass

from kungfu_chess.model.piece_kind import PieceKind


@dataclass(frozen=True)
class PromotionRequestedMessage:
    """
    Represents a request to promote a pawn.

    Contains only the data required to perform
    the promotion operation.
    """

    piece_id: int
    chosen_kind: PieceKind