from kungfu_chess.engine.services.jump_service import PENDING_PAWN_PROMOTION, PIECE_IN_MOTION
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.realtime.state_timer import StateTimer
from kungfu_chess.rules.chess_pawn_end_handler import ChessPawnEndHandler
from kungfu_chess.rules.move_validation import MoveValidation
from kungfu_chess.rules.pawn_end_outcome import PendingPawnPromotion
from kungfu_chess.view.runtime_role import RuntimeRole
from kungfu_chess.view.snapshot_builder import SnapshotBuilder
from tests.helpers.engine_fakes import FakeConfigRepository, FakeMotionFactory, FakeRuleEngine, FakeStateTimer, FixedJumpDurationResolver, JumpLifecycleTransitionResolver, TrackingMotionFactory
from tests.helpers.engine_test_factory import create_jump_collision_engine, create_jump_engine
from tests.helpers.engine_wiring import build_engine_context


def test_request_jump_sets_jump_state():
    engine, state, piece, _ = create_jump_engine()

    result = engine.request_jump(piece.id)

    assert result.is_accepted is True
    assert piece.state == PieceState.JUMP
    assert piece.cell == Position(0, 0)
    assert piece.has_moved is False


def test_request_jump_does_not_create_motion():
    motion_factory = TrackingMotionFactory()
    engine, _, piece, motion_factory = create_jump_engine(motion_factory)

    engine.request_jump(piece.id)

    assert motion_factory.calls == []
    assert engine.realtime_arbiter.has_motion(piece.id) is False


def test_jump_does_not_move_piece():
    engine, state, piece, _ = create_jump_engine()
    board_snapshot = {
        position: board_piece.id
        for position, board_piece in state.board.pieces_by_position.items()
    }

    engine.request_jump(piece.id)

    assert {
        position: board_piece.id
        for position, board_piece in state.board.pieces_by_position.items()
    } == board_snapshot
    assert state.board.get_piece_by_position(piece.cell) is piece


def test_request_jump_rejected_while_promotion_pending():
    engine, state, piece, _ = create_jump_engine()
    state.pending_pawn_promotion = PendingPawnPromotion(
        piece_id=99,
        allowed_kinds=ChessPawnEndHandler.PROMOTION_KINDS,
    )

    result = engine.request_jump(piece.id)

    assert result.is_accepted is False
    assert result.reason == PENDING_PAWN_PROMOTION
    assert piece.state == PieceState.IDLE


def test_request_jump_rejected_while_piece_is_in_motion():
    engine, state, piece, _ = create_jump_engine()

    engine.realtime_arbiter.start_motion(
        Motion(1, Position(0, 0), Position(0, 1), duration_ms=1000)
    )

    result = engine.request_jump(piece.id)

    assert result.is_accepted is False
    assert result.reason == PIECE_IN_MOTION
    assert piece.state == PieceState.IDLE


def test_request_jump_creates_active_jump_window():
    engine, _, piece, _ = create_jump_engine()
    tracker = engine._jump_service._jump_window_tracker

    engine.request_jump(piece.id)

    assert tracker.is_active_at(piece.id, 0) is True
    assert tracker.is_active_at(piece.id, 499) is True
    assert tracker.is_active_at(piece.id, 500) is False


def test_request_jump_does_not_set_has_moved():
    engine, _, piece, _ = create_jump_engine()

    engine.request_jump(piece.id)

    assert piece.has_moved is False



def test_jumping_defender_captures_enemy_landing_on_cell():
    engine, state, defender, attacker = create_jump_collision_engine()

    engine.request_jump(defender.id)
    engine.realtime_arbiter.start_motion(
        Motion(2, Position(0, 0), Position(0, 3), duration_ms=400)
    )

    captured = engine.wait(400)

    assert captured == [attacker]
    assert state.board.get_piece_by_id(defender.id) is defender
    assert state.board.get_piece_by_position(Position(0, 3)) is defender
    assert state.board.get_piece_by_id(attacker.id) is None
    assert defender.has_moved is False


def test_expired_jump_window_leaves_defender_vulnerable():
    engine, state, defender, attacker = create_jump_collision_engine()

    engine.request_jump(defender.id)
    engine.wait(600)
    engine.realtime_arbiter.start_motion(
        Motion(2, Position(0, 0), Position(0, 3), duration_ms=400)
    )

    captured = engine.wait(400)

    assert captured == [defender]
    assert state.board.get_piece_by_id(defender.id) is None
    assert state.board.get_piece_by_position(Position(0, 3)).id == 2


def test_jumping_king_capturing_enemy_does_not_end_game():
    board = Board(8, 8)
    defender = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.KING,
        cell=Position(0, 3),
    )
    attacker = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.ROOK,
        cell=Position(0, 0),
    )
    board.add_piece(defender)
    board.add_piece(attacker)
    state = GameState(board)

    context = build_engine_context(
        state,
        FakeRuleEngine(MoveValidation(True, "ok")),
        motion_factory=FakeMotionFactory(),
        config_repository=FakeConfigRepository(),
        state_timer=FakeStateTimer(),
        state_transition_resolver=JumpLifecycleTransitionResolver(),
        jump_duration_resolver=FixedJumpDurationResolver(500),
    )
    engine = context.engine

    engine.request_jump(defender.id)
    engine.realtime_arbiter.start_motion(
        Motion(2, Position(0, 0), Position(0, 3), duration_ms=400)
    )

    captured = engine.wait(400)

    assert captured == [attacker]
    assert state.game_over is False
    assert state.board.get_piece_by_id(defender.id) is defender


def test_snapshot_shows_jump_state_after_request_jump():
    engine, state, piece, _ = create_jump_engine()
    builder = SnapshotBuilder(get_runtime_progress=engine.runtime_progress)

    engine.request_jump(piece.id)
    snapshot = builder.build(state)

    piece_snapshot = next(
        snapshot_piece
        for snapshot_piece in snapshot.pieces
        if snapshot_piece.piece_id == piece.id
    )

    assert piece_snapshot.state == PieceState.JUMP
    assert piece_snapshot.runtime_progress[RuntimeRole.ACTIVE_ABILITY] == 0.0


def test_runtime_progress_returns_active_ability_for_jump():
    engine, _, piece, _ = create_jump_engine()

    engine.request_jump(piece.id)

    assert engine.runtime_progress(piece.id) == {
        RuntimeRole.ACTIVE_ABILITY: 0.0,
    }


def test_runtime_progress_advances_active_ability_during_jump():
    engine, _, piece, _ = create_jump_engine(jump_duration_ms=500)

    engine.request_jump(piece.id)
    engine.wait(250)

    assert engine.runtime_progress(piece.id) == {
        RuntimeRole.ACTIVE_ABILITY: 0.5,
    }


def test_runtime_progress_returns_recovery_after_jump_finishes():
    engine, _, piece, _ = create_jump_engine(
        jump_duration_ms=500,
        state_timer=StateTimer(),
    )

    engine.request_jump(piece.id)
    engine.wait(500)

    assert piece.state == "short_rest"
    assert engine.runtime_progress(piece.id) == {RuntimeRole.RECOVERY: 0.0}

    engine.wait(750)

    assert engine.runtime_progress(piece.id) == {RuntimeRole.RECOVERY: 0.5}


def test_timed_state_progress_returns_jump_progress_after_request_jump():
    engine, _, piece, _ = create_jump_engine()

    engine.request_jump(piece.id)

    assert engine.timed_state_progress(piece.id) == 0.0


def test_timed_state_progress_advances_during_wait():
    engine, _, piece, _ = create_jump_engine(jump_duration_ms=500)

    engine.request_jump(piece.id)
    engine.wait(250)

    assert engine.timed_state_progress(piece.id) == 0.5


def test_timed_state_progress_uses_state_timer_after_jump_finishes():
    engine, _, piece, _ = create_jump_engine(
        jump_duration_ms=500,
        state_timer=StateTimer(),
    )

    engine.request_jump(piece.id)
    engine.wait(500)

    assert piece.state == "short_rest"
    assert engine.timed_state_progress(piece.id) == 0.0

    engine.wait(750)

    assert engine.timed_state_progress(piece.id) == 0.5


def test_jump_transitions_to_short_rest_after_duration():
    engine, _, piece, _ = create_jump_engine(jump_duration_ms=500)

    engine.request_jump(piece.id)
    assert piece.state == PieceState.JUMP

    engine.wait(499)
    assert piece.state == PieceState.JUMP

    engine.wait(1)
    assert piece.state == "short_rest"


def test_move_state_unchanged_by_jump_lifecycle():
    engine, _, piece, _ = create_jump_engine()

    engine.request_move(Position(0, 0), Position(0, 1))

    assert piece.state == PieceState.MOVING
    assert engine.realtime_arbiter.has_motion(piece.id) is True


def test_jumping_defender_capturing_king_ends_game():
    board = Board(8, 8)
    defender = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.KNIGHT,
        cell=Position(0, 3),
    )
    attacker = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.KING,
        cell=Position(0, 0),
    )
    board.add_piece(defender)
    board.add_piece(attacker)
    state = GameState(board)

    context = build_engine_context(
        state,
        FakeRuleEngine(MoveValidation(True, "ok")),
        motion_factory=FakeMotionFactory(),
        config_repository=FakeConfigRepository(),
        state_timer=FakeStateTimer(),
        state_transition_resolver=JumpLifecycleTransitionResolver(),
        jump_duration_resolver=FixedJumpDurationResolver(500),
    )
    engine = context.engine

    engine.request_jump(defender.id)
    engine.realtime_arbiter.start_motion(
        Motion(2, Position(0, 0), Position(0, 3), duration_ms=400)
    )

    captured = engine.wait(400)

    assert captured == [attacker]
    assert state.game_over is True
    assert state.board.get_piece_by_id(defender.id) is defender

