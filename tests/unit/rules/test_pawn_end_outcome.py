from kungfu_chess.rules.pawn_end_outcome import PawnEndOutcome
from kungfu_chess.model.piece_kind import PieceKind
import pytest


def test_no_action_outcome_has_no_fields_set():
    outcome = PawnEndOutcome.no_action()

    assert outcome.new_kind is None
    assert outcome.pending_choice_kinds is None
    assert outcome.blocks_state_transition is False


def test_immediate_outcome_sets_new_kind():
    outcome = PawnEndOutcome.immediate(PieceKind.QUEEN)

    assert outcome.new_kind == PieceKind.QUEEN
    assert outcome.pending_choice_kinds is None


def test_pending_choice_sets_allowed_kinds_and_blocks_transition():
    kinds = frozenset({PieceKind.QUEEN, PieceKind.ROOK})

    outcome = PawnEndOutcome.pending_choice(kinds)

    assert outcome.pending_choice_kinds == kinds
    assert outcome.blocks_state_transition is True
    assert outcome.new_kind is None


def test_new_kind_and_pending_choice_together_are_invalid():
    with pytest.raises(ValueError):
        PawnEndOutcome(
            new_kind=PieceKind.QUEEN,
            pending_choice_kinds=frozenset({PieceKind.ROOK}),
            blocks_state_transition=True,
        )


def test_pending_choice_without_block_is_invalid():
    with pytest.raises(ValueError):
        PawnEndOutcome(
            pending_choice_kinds=frozenset({PieceKind.QUEEN}),
            blocks_state_transition=False,
        )
