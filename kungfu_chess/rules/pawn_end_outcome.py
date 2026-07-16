from dataclasses import dataclass

from kungfu_chess.model.piece_kind import PieceKind


@dataclass(frozen=True, slots=True)
class PawnEndOutcome:
    """
    Result of a pawn reaching the end rank.

    Phase 1:
    - new_kind represents an immediate transformation.

    Future modes may add deferred choices or other outcomes.
    """

    new_kind: PieceKind | None = None
