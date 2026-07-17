from dataclasses import dataclass

from kungfu_chess.model.piece_kind import PieceKind


@dataclass(frozen=True, slots=True)
class PromotePawnCommand:
    """
    Carries a pawn promotion choice from input to the controller.

    This command contains data only. It does not validate the choice
    or modify game state.
    """

    piece_id: int
    chosen_kind: PieceKind
