from dataclasses import dataclass

from kungfu_chess.model.piece_kind import PieceKind


@dataclass(frozen=True, slots=True)
class PendingPawnPromotion:
    """
    Describes a pawn waiting for a promotion piece choice.

    Stored on GameState until the choice is submitted to the engine.
    """

    piece_id: int
    allowed_kinds: frozenset[PieceKind]


@dataclass(frozen=True, slots=True)
class PawnEndOutcome:
    """
    Result of a pawn reaching the end rank.

    Immediate transformation uses new_kind.
    Deferred player choice uses pending_choice_kinds with
    blocks_state_transition=True.

    new_kind and pending_choice_kinds are mutually exclusive.
    """

    new_kind: PieceKind | None = None
    pending_choice_kinds: frozenset[PieceKind] | None = None
    blocks_state_transition: bool = False

    def __post_init__(self) -> None:
        has_immediate = self.new_kind is not None
        has_pending = self.pending_choice_kinds is not None

        if has_immediate and has_pending:
            raise ValueError(
                "PawnEndOutcome cannot set both new_kind and pending_choice_kinds"
            )

        if has_pending and not self.blocks_state_transition:
            raise ValueError(
                "PawnEndOutcome with pending_choice_kinds must block state transition"
            )

    @classmethod
    def no_action(cls) -> "PawnEndOutcome":
        return cls()

    @classmethod
    def immediate(cls, kind: PieceKind) -> "PawnEndOutcome":
        return cls(new_kind=kind)

    @classmethod
    def pending_choice(cls, kinds: frozenset[PieceKind]) -> "PawnEndOutcome":
        return cls(
            pending_choice_kinds=kinds,
            blocks_state_transition=True,
        )
