import pytest

from kungfu_chess.engine.services.jump_service import PENDING_PAWN_PROMOTION
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.rules.auto_promote_queen_handler import AutoPromoteQueenHandler
from kungfu_chess.rules.chess_pawn_end_handler import ChessPawnEndHandler
from kungfu_chess.rules.move_validation import MoveValidation
from kungfu_chess.rules.pawn_end_outcome import PendingPawnPromotion
from tests.helpers.engine_fakes import FakeConfigRepository, FakeMotionFactory, FakeRuleEngine, FakeStateTimer, FakeStateTransitionResolver, TrackingStateTransitionResolver
from tests.helpers.engine_test_factory import board_with_pending_promotion, create_promotion_engine, land_white_pawn_on_promotion_rank
from tests.helpers.engine_wiring import build_engine_context



def test_pawn_promotion_sets_queen_kind_after_completion():
    board = Board(8, 8)
    pawn = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.PAWN,
        cell=Position(1, 3),
    )
    board.add_piece(pawn)
    state = GameState(board)

    context = build_engine_context(
        state,
        FakeRuleEngine(MoveValidation(True, "ok")),
        motion_factory=FakeMotionFactory(),
        config_repository=FakeConfigRepository(),
        state_timer=FakeStateTimer(),
        state_transition_resolver=FakeStateTransitionResolver(),
        pawn_end_handler=AutoPromoteQueenHandler(),
    )
    engine = context.engine

    engine.realtime_arbiter.start_motion(
        Motion(1, Position(1, 3), Position(0, 3), duration_ms=1000)
    )

    engine.wait(1000)

    assert pawn.kind == PieceKind.QUEEN
    assert pawn.has_moved is True
    assert state.board.get_piece_by_position(Position(0, 3)) is pawn



def test_pawn_reaching_end_with_chess_handler_does_not_auto_promote():
    board = Board(8, 8)
    pawn = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.PAWN,
        cell=Position(1, 3),
    )
    board.add_piece(pawn)
    state = GameState(board)
    context = create_promotion_engine(state, pawn, ChessPawnEndHandler())
    engine = context.engine

    engine.realtime_arbiter.start_motion(
        Motion(1, Position(1, 3), Position(0, 3), duration_ms=1000)
    )
    engine.wait(1000)

    assert pawn.kind == PieceKind.PAWN
    assert pawn.has_moved is True


def test_pawn_reaching_end_sets_pending_promotion_state():
    board = Board(8, 8)
    pawn = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.PAWN,
        cell=Position(1, 3),
    )
    board.add_piece(pawn)
    state = GameState(board)
    context = create_promotion_engine(state, pawn, ChessPawnEndHandler())
    engine = context.engine

    engine.realtime_arbiter.start_motion(
        Motion(1, Position(1, 3), Position(0, 3), duration_ms=1000)
    )
    engine.wait(1000)

    assert state.pending_pawn_promotion is not None
    assert state.pending_pawn_promotion.piece_id == pawn.id
    assert state.pending_pawn_promotion.allowed_kinds == ChessPawnEndHandler.PROMOTION_KINDS


def test_pawn_landing_with_pending_keeps_pawn_kind_and_defers_transition():
    _, state, pawn, transition_resolver = land_white_pawn_on_promotion_rank()

    assert pawn.kind == PieceKind.PAWN
    assert state.pending_pawn_promotion is not None
    assert state.pending_pawn_promotion.piece_id == pawn.id
    assert transition_resolver.calls == []


def test_request_move_for_other_piece_rejected_while_promotion_pending():
    engine, _, pawn, rook = board_with_pending_promotion()

    result = engine.request_move(rook.cell, Position(4, 5))

    assert result.is_accepted is False
    assert result.reason == PENDING_PAWN_PROMOTION


def test_request_move_for_promoting_pawn_rejected_while_pending():
    engine, _, pawn, _ = board_with_pending_promotion()

    result = engine.request_move(pawn.cell, Position(0, 4))

    assert result.is_accepted is False
    assert result.reason == PENDING_PAWN_PROMOTION


@pytest.mark.parametrize(
    "chosen_kind",
    [
        PieceKind.QUEEN,
        PieceKind.ROOK,
        PieceKind.BISHOP,
        PieceKind.KNIGHT,
    ],
)
def test_submit_promotion_choice_applies_kind_clears_pending_and_transitions(
    chosen_kind,
):
    board = Board(8, 8)
    pawn = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.PAWN,
        cell=Position(0, 3),
    )
    board.add_piece(pawn)
    state = GameState(board)
    transition_resolver = TrackingStateTransitionResolver()
    context = create_promotion_engine(
        state,
        pawn,
        ChessPawnEndHandler(),
        transition_resolver,
    )

    state.pending_pawn_promotion = PendingPawnPromotion(
        piece_id=pawn.id,
        allowed_kinds=ChessPawnEndHandler.PROMOTION_KINDS,
    )

    result = context.submit_pawn_promotion_choice(pawn.id, chosen_kind)

    assert result.is_accepted is True
    assert pawn.kind == chosen_kind
    assert state.pending_pawn_promotion is None
    assert transition_resolver.calls
    assert pawn.state == PieceState.IDLE


def test_submit_promotion_choice_queen_changes_kind():
    board = Board(8, 8)
    pawn = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.PAWN,
        cell=Position(0, 3),
    )
    board.add_piece(pawn)
    state = GameState(board)
    context = create_promotion_engine(state, pawn, ChessPawnEndHandler())

    state.pending_pawn_promotion = PendingPawnPromotion(
        piece_id=pawn.id,
        allowed_kinds=ChessPawnEndHandler.PROMOTION_KINDS,
    )

    result = context.submit_pawn_promotion_choice(pawn.id, PieceKind.QUEEN)

    assert result.is_accepted is True
    assert pawn.kind == PieceKind.QUEEN
    assert state.pending_pawn_promotion is None


def test_submit_promotion_choice_knight_changes_kind():
    board = Board(8, 8)
    pawn = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.PAWN,
        cell=Position(0, 3),
    )
    board.add_piece(pawn)
    state = GameState(board)
    context = create_promotion_engine(state, pawn, ChessPawnEndHandler())

    state.pending_pawn_promotion = PendingPawnPromotion(
        piece_id=pawn.id,
        allowed_kinds=ChessPawnEndHandler.PROMOTION_KINDS,
    )

    result = context.submit_pawn_promotion_choice(pawn.id, PieceKind.KNIGHT)

    assert result.is_accepted is True
    assert pawn.kind == PieceKind.KNIGHT
    assert state.pending_pawn_promotion is None


def test_submit_invalid_promotion_choice_is_rejected():
    board = Board(8, 8)
    pawn = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.PAWN,
        cell=Position(0, 3),
    )
    board.add_piece(pawn)
    state = GameState(board)
    context = create_promotion_engine(state, pawn, ChessPawnEndHandler())

    state.pending_pawn_promotion = PendingPawnPromotion(
        piece_id=pawn.id,
        allowed_kinds=ChessPawnEndHandler.PROMOTION_KINDS,
    )

    result = context.submit_pawn_promotion_choice(pawn.id, PieceKind.PAWN)

    assert result.is_accepted is False
    assert result.reason == "invalid_promotion_choice"
    assert pawn.kind == PieceKind.PAWN
    assert state.pending_pawn_promotion is not None

