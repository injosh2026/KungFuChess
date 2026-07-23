from kungfu_chess.config.piece_config_repository import PieceConfigRepository
from kungfu_chess.config.state_config import GraphicsConfig, PhysicsConfig, StateConfig
from kungfu_chess.engine.services.jump_service import (
    PENDING_PAWN_PROMOTION,
    PIECE_IN_COOLDOWN,
    PIECE_IN_MOTION,
)
from kungfu_chess.engine.services.motion_completion_service import (
    MotionCompletionService,
)
from kungfu_chess.engine.state_transition_resolver import StateTransitionResolver
from tests.helpers.engine_wiring import CompleteSimulationService, EngineTestContext, build_engine_context
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.realtime.movement_duration import MovementDurationCalculator
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter
from kungfu_chess.realtime.state_timer import StateTimer
from kungfu_chess.rules.auto_promote_queen_handler import AutoPromoteQueenHandler
from kungfu_chess.rules.chess_pawn_end_handler import ChessPawnEndHandler
from kungfu_chess.rules.jump_rule import JumpRule
from kungfu_chess.rules.move_validation import MoveValidation
from kungfu_chess.rules.pawn_end_outcome import PendingPawnPromotion
from kungfu_chess.view.runtime_role import RuntimeRole
from kungfu_chess.view.snapshot_builder import SnapshotBuilder

import pytest


class FixedJumpDurationResolver:

    def __init__(self, duration_ms: int):
        self._duration_ms = duration_ms

    def duration_ms(self, piece_code, jump_state_name):
        return self._duration_ms


class JumpLifecycleTransitionResolver:

    def resolve(self, piece_code, current_state):
        if current_state == "jump":
            return "short_rest"
        if current_state == "short_rest":
            return "idle"
        return current_state


class FakeRuleEngine:

    def __init__(self, validation):
        self.validation = validation
        self.called = False

    def validate_move(self, board, source, destination):
        self.called = True
        return self.validation


class FakeArbiter:

    def __init__(self):
        self.called_with = None

    def active_motions(self):
        return ()

    def advance_time(self, milliseconds):
        self.called_with = milliseconds
        return []


class FakeMotionFactory:

    def create(self, piece, source, target):
        return Motion(
            piece.id,
            source,
            target,
            1000
        )


class TrackingMotionFactory:

    def __init__(self):
        self.calls = []

    def create(self, piece, source, target):
        self.calls.append((piece.id, source, target))
        return Motion(
            piece.id,
            source,
            target,
            duration_ms=1000,
        )


class FakeConfigRepository:

    def __init__(self, move_command_state="move", jump_command_state="jump"):
        self.move_command_state = move_command_state
        self.jump_command_state = jump_command_state

    def get_move_command_state(self, piece_code):
        return self.move_command_state

    def get_jump_command_state(self, piece_code):
        return self.jump_command_state

    def load_state(self, piece_code, state_name):
        if state_name == "jump":
            return StateConfig(
                physics=PhysicsConfig(
                    speed_m_per_sec=3.0,
                    next_state_when_finished="short_rest",
                ),
                graphics=GraphicsConfig(frames_per_sec=8, is_loop=False),
            )

        if state_name == "short_rest":
            return StateConfig(
                physics=PhysicsConfig(
                    speed_m_per_sec=0.0,
                    next_state_when_finished="idle",
                    duration_ms=1500,
                ),
                graphics=GraphicsConfig(frames_per_sec=8, is_loop=True),
            )

        return StateConfig(
            physics=PhysicsConfig(
                speed_m_per_sec=0.0,
                next_state_when_finished=state_name,
            ),
            graphics=GraphicsConfig(frames_per_sec=12, is_loop=True),
        )


class FakeStateTransitionResolver:

    def resolve(self, piece_code, current_state):
        return "idle"


class TrackingStateTransitionResolver:

    def __init__(self, next_state="idle"):
        self.calls = []
        self.next_state = next_state

    def resolve(self, piece_code, current_state):
        self.calls.append((piece_code, current_state))
        return self.next_state


class FakeStateTimer:

    def start(self, piece_id, duration_ms):
        pass

    def advance(self, milliseconds, *, only_piece_ids=None):
        return []

    def progress(self, piece_id):
        return None

    def active_piece_ids(self):
        return []

    def has_active_timer(self, piece_id):
        return False


def create_engine(validation):

    board = Board(8, 8)

    source_piece = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0)
    )

    board.add_piece(source_piece)

    state = GameState(board)

    rule_engine = FakeRuleEngine(validation)

    context = build_engine_context(
        state,
        rule_engine,
        motion_factory=FakeMotionFactory(),
        config_repository=FakeConfigRepository(),
        state_timer=FakeStateTimer(),
        state_transition_resolver=FakeStateTransitionResolver(),
    )

    return context.engine, state, rule_engine


def test_game_over_rejects_move():

    engine, state, rule_engine = create_engine(MoveValidation(True, "ok"))

    state.game_over = True

    result = engine.request_move(Position(0, 0), Position(0, 1))

    assert result.is_accepted is False
    assert result.reason == "game_over"

    assert rule_engine.called is False


def test_valid_move_returns_ok():

    engine, _, rule_engine = create_engine(MoveValidation(True, "ok"))

    result = engine.request_move(Position(0, 0), Position(0, 1))

    assert result.is_accepted is True
    assert result.reason == "ok"

    assert rule_engine.called is True


def create_jump_engine(
    motion_factory=None,
    jump_duration_ms=500,
    state_timer=None,
):
    board = Board(8, 8)

    piece = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.KNIGHT,
        cell=Position(0, 0),
    )

    board.add_piece(piece)

    state = GameState(board)

    rule_engine = FakeRuleEngine(
        MoveValidation(True, "ok")
    )

    state_timer = state_timer or FakeStateTimer()

    motion_factory = motion_factory or TrackingMotionFactory()

    context = build_engine_context(
        state,
        rule_engine,
        motion_factory=motion_factory,
        config_repository=FakeConfigRepository(),
        state_timer=state_timer,
        state_transition_resolver=JumpLifecycleTransitionResolver(),
        jump_duration_resolver=FixedJumpDurationResolver(jump_duration_ms),
    )

    return context.engine, state, piece, motion_factory

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


def create_jump_collision_engine():
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
    return context.engine, state, defender, attacker


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


def test_invalid_move_returns_reason():

    engine, _, _ = create_engine(MoveValidation(False, "illegal_piece_move"))

    result = engine.request_move(Position(0, 0), Position(3, 3))

    assert result.is_accepted is False
    assert result.reason == "illegal_piece_move"


def create_motion():

    return Motion(
        piece_id=1, start=Position(0, 0), target=Position(0, 1), duration_ms=1000
    )


def test_cannot_start_move_when_same_piece_is_in_motion():

    engine, _, rule_engine = create_engine(MoveValidation(True, "ok"))

    engine.realtime_arbiter.start_motion(create_motion())

    result = engine.request_move(Position(0, 0), Position(0, 1))

    assert result.is_accepted is False
    assert result.reason == PIECE_IN_MOTION

    assert rule_engine.called is True


def test_other_piece_can_move_while_piece_is_in_motion():

    engine, state, _ = create_engine(MoveValidation(True, "ok"))

    second_piece = Piece(
        id=2,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(2, 0),
    )
    state.board.add_piece(second_piece)

    engine.request_move(Position(0, 0), Position(0, 1))

    result = engine.request_move(Position(2, 0), Position(2, 1))

    assert result.is_accepted is True
    assert len(engine.active_motions()) == 2


def test_valid_move_without_source_piece_raises_error():

    engine, state, _ = create_engine(MoveValidation(True, "ok"))

    state.board.remove_piece(Position(0,0))

    try:
        engine.request_move(Position(0,0), Position(0,1))
        assert False
    except RuntimeError as e:
        assert str(e) == "Validated move without source piece"


def test_wait_advances_all_active_motions():

    engine, state, _ = create_engine(MoveValidation(True, "ok"))

    second_piece = Piece(
        id=2,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(2, 0),
    )
    state.board.add_piece(second_piece)

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.request_move(Position(2, 0), Position(2, 1))

    engine.wait(500)

    motions = {motion.piece_id: motion for motion in engine.active_motions()}
    assert motions[1].elapsed_ms == 500
    assert motions[2].elapsed_ms == 500


def test_wait_moves_piece_when_motion_completes():

    engine, state, _ = create_engine(
        MoveValidation(True, "ok")
    )

    engine.request_move(
        Position(0, 0),
        Position(0, 1)
    )

    engine.wait(1000)

    assert state.board.get_piece_by_position(
        Position(0, 0)
    ) is None

    assert state.board.get_piece_by_position(
        Position(0, 1)
    ) is not None


def test_wait_resolves_two_completed_motions_in_same_tick():

    engine, state, _ = create_engine(MoveValidation(True, "ok"))

    second_piece = Piece(
        id=2,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(2, 0),
    )
    state.board.add_piece(second_piece)

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.request_move(Position(2, 0), Position(2, 1))

    engine.wait(1000)

    assert state.board.get_piece_by_position(Position(0, 1)) is not None
    assert state.board.get_piece_by_position(Position(2, 1)) is not None
    assert engine.active_motions() == ()


def test_later_arrival_captures_standing_enemy():
    engine, state, _ = create_engine(MoveValidation(True, "ok"))

    enemy = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.ROOK,
        cell=Position(0, 3),
    )
    state.board.add_piece(enemy)

    engine.request_move(Position(0, 0), Position(0, 3))
    captured = engine.wait(1000)

    assert captured == [enemy]
    assert state.board.get_piece_by_position(Position(0, 3)).id == 1
    assert state.board.get_piece_by_id(2) is None


def test_later_arrival_to_same_cell_captures_earlier_arrival():
    board = Board(8, 8)
    earlier = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0),
    )
    later = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.ROOK,
        cell=Position(2, 0),
    )
    board.add_piece(earlier)
    board.add_piece(later)
    state = GameState(board)

    engine = _build_basic_engine(state).engine

    target = Position(0, 3)
    engine.realtime_arbiter.start_motion(
        Motion(1, Position(0, 0), target, duration_ms=500)
    )
    engine.realtime_arbiter.start_motion(
        Motion(2, Position(2, 0), target, duration_ms=1000)
    )

    captured = engine.wait(1000)

    assert captured == [earlier]
    assert state.board.get_piece_by_position(target).id == 2
    assert state.board.get_piece_by_id(1) is None


def test_same_cell_same_duration_uses_piece_id_tie_break():
    board = Board(8, 8)
    earlier = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0),
    )
    later = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.ROOK,
        cell=Position(2, 0),
    )
    board.add_piece(earlier)
    board.add_piece(later)
    state = GameState(board)

    engine = _build_basic_engine(state).engine

    target = Position(0, 3)
    engine.realtime_arbiter.start_motion(
        Motion(1, Position(0, 0), target, duration_ms=1000)
    )
    engine.realtime_arbiter.start_motion(
        Motion(2, Position(2, 0), target, duration_ms=1000)
    )

    captured = engine.wait(1000)

    assert captured == [earlier]
    assert state.board.get_piece_by_position(target).id == 2
    assert state.board.get_piece_by_id(1) is None


def test_capturing_king_ends_game():

    engine, state, _ = create_engine(
        MoveValidation(True, "ok")
    )

    king = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.KING,
        cell=Position(0, 1)
    )

    state.board.add_piece(king)

    engine.request_move(
        Position(0, 0),
        Position(0, 1)
    )

    captured = engine.wait(1000)

    assert captured == [king]
    assert state.game_over is True


def test_wait_delegates_to_real_time_arbiter():

    board = Board(8, 8)

    state = GameState(board)

    arbiter = FakeArbiter()

    context = build_engine_context(
        state,
        FakeRuleEngine(MoveValidation(True, "ok")),
        motion_factory=FakeMotionFactory(),
        config_repository=FakeConfigRepository(),
        state_timer=FakeStateTimer(),
        state_transition_resolver=FakeStateTransitionResolver(),
        realtime_arbiter=arbiter,
    )
    engine = context.engine

    engine.wait(700)

    assert arbiter.called_with == 700


import json
from pathlib import Path

from kungfu_chess.rules.move_validation import MoveValidation as MV

PIECE_CODE = "RW"
LONG_REST_DURATION_MS = 2000
MOTION_DURATION_MS = 1000


def write_piece_defaults(root: Path) -> None:
    defaults = {"initial_state": "idle", "move_command_state": "move", "jump_command_state": "jump"}
    defaults_path = root / "pieces2" / "piece_defaults.json"
    defaults_path.parent.mkdir(parents=True, exist_ok=True)
    defaults_path.write_text(
        json.dumps(defaults),
        encoding="utf-8",
    )


def write_state_config(
    root: Path,
    piece_code: str,
    state_name: str,
    next_state: str,
    speed: float = 1.5,
    duration_ms: int | None = None,
) -> None:
    state_dir = root / "pieces2" / piece_code / "states" / state_name
    state_dir.mkdir(parents=True)
    physics = {
        "speed_m_per_sec": speed,
        "next_state_when_finished": next_state,
    }
    if duration_ms is not None:
        physics["duration_ms"] = duration_ms
    config = {
        "physics": physics,
        "graphics": {"frames_per_sec": 12, "is_loop": True},
    }
    (state_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")


def create_configured_engine(
    root: Path,
    move_next_state: str,
    extra_states: tuple[tuple[str, str, float, int | None], ...] = (),
):
    write_piece_defaults(root)
    write_state_config(root, PIECE_CODE, "idle", "idle", speed=0.0)
    write_state_config(root, PIECE_CODE, "move", move_next_state)
    write_state_config(
        root,
        PIECE_CODE,
        "jump",
        "short_rest",
        speed=3.0,
        duration_ms=500,
    )
    for state_name, next_state, speed, duration_ms in extra_states:
        write_state_config(
            root,
            PIECE_CODE,
            state_name,
            next_state,
            speed=speed,
            duration_ms=duration_ms,
        )

    board = Board(8, 8)
    piece = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0),
    )
    board.add_piece(piece)
    state = GameState(board)

    repository = PieceConfigRepository(root)
    resolver = StateTransitionResolver(repository)

    context = build_engine_context(
        state,
        FakeRuleEngine(MV(True, "ok")),
        motion_factory=FakeMotionFactory(),
        config_repository=repository,
        state_timer=StateTimer(),
        state_transition_resolver=resolver,
        assets_root=root,
    )
    return context.engine, piece


def test_completed_move_transitions_to_idle_from_config(tmp_path):
    engine, piece = create_configured_engine(tmp_path, "idle")

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    assert piece.state == "idle"


def test_completed_move_transitions_to_long_rest_from_config(tmp_path):
    engine, piece = create_configured_engine(
        tmp_path,
        "long_rest",
        extra_states=(("long_rest", "idle", 0.0, LONG_REST_DURATION_MS),),
    )

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    assert piece.state == "long_rest"


def test_long_rest_with_duration_transitions_to_idle_after_timer(tmp_path):
    engine, piece = create_configured_engine(
        tmp_path,
        "long_rest",
        extra_states=(("long_rest", "idle", 0.0, LONG_REST_DURATION_MS),),
    )

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(MOTION_DURATION_MS)

    assert piece.state == "long_rest"

    engine.wait(500)
    assert piece.state == "long_rest"

    engine.wait(LONG_REST_DURATION_MS - 500)
    assert piece.state == "idle"


def test_short_rest_without_duration_passes_through_to_idle(tmp_path):
    engine, piece = create_configured_engine(
        tmp_path,
        "short_rest",
        extra_states=(("short_rest", "idle", 0.0, None),),
    )

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    assert piece.state == "idle"


def test_completed_move_transitions_to_custom_state_from_config(tmp_path):
    engine, piece = create_configured_engine(
        tmp_path,
        "custom_state",
        extra_states=(("custom_state", "custom_state", 0.0, None),),
    )

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    assert piece.state == "custom_state"


def test_state_timer_progress_via_engine(tmp_path):
    engine, piece = create_configured_engine(
        tmp_path,
        "long_rest",
        extra_states=(("long_rest", "idle", 0.0, LONG_REST_DURATION_MS),),
    )

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(MOTION_DURATION_MS)

    assert engine.state_timer_progress(piece.id) == 0.5

    engine.wait(LONG_REST_DURATION_MS // 2)
    assert engine.state_timer_progress(piece.id) is None
    assert piece.state == "idle"


def test_completed_move_uses_bundled_config_for_long_rest():
    board = Board(8, 8)
    piece = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.QUEEN,
        cell=Position(0, 0),
    )
    board.add_piece(piece)
    state = GameState(board)

    repository = PieceConfigRepository(Path("assets"))
    resolver = StateTransitionResolver(repository)
    context = build_engine_context(
        state,
        FakeRuleEngine(MV(True, "ok")),
        motion_factory=FakeMotionFactory(),
        config_repository=repository,
        state_timer=StateTimer(),
        state_transition_resolver=resolver,
        assets_root=Path("assets"),
    )
    engine = context.engine

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    assert piece.state == "long_rest"


def test_motion_still_provides_visual_position_in_snapshot(tmp_path):
    from kungfu_chess.view.snapshot_builder import SnapshotBuilder

    engine, _piece = create_configured_engine(tmp_path, "idle")

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(500)

    snapshot = SnapshotBuilder().build(
        engine.game_state,
        motions=engine.active_motions(),
    )

    assert snapshot.pieces[0].state == "move"
    assert snapshot.pieces[0].visual_position is not None


def test_request_move_rejects_piece_in_cooldown(tmp_path):
    engine, piece = create_configured_engine(
        tmp_path,
        "long_rest",
        extra_states=(("long_rest", "idle", 0.0, LONG_REST_DURATION_MS),),
    )

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    result = engine.request_move(Position(0, 1), Position(0, 2))

    assert result.is_accepted is False
    assert result.reason == PIECE_IN_COOLDOWN


def test_request_move_allowed_after_cooldown_expires(tmp_path):
    engine, piece = create_configured_engine(
        tmp_path,
        "long_rest",
        extra_states=(("long_rest", "idle", 0.0, LONG_REST_DURATION_MS),),
    )

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(MOTION_DURATION_MS)
    engine.wait(LONG_REST_DURATION_MS)

    result = engine.request_move(Position(0, 1), Position(0, 2))

    assert result.is_accepted is True
    assert result.reason == "ok"


def test_short_rest_without_duration_allows_immediate_next_move(tmp_path):
    engine, piece = create_configured_engine(
        tmp_path,
        "short_rest",
        extra_states=(("short_rest", "idle", 0.0, None),),
    )

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    result = engine.request_move(Position(0, 1), Position(0, 2))

    assert result.is_accepted is True


def test_get_legal_moves_unchanged_during_cooldown(tmp_path):
    from kungfu_chess.rules.rule_engine import RuleEngine
    from kungfu_chess.rules.rook_rule import RookRule
    from kungfu_chess.model.piece_kind import PieceKind as PK

    engine, piece = create_configured_engine(
        tmp_path,
        "long_rest",
        extra_states=(("long_rest", "idle", 0.0, LONG_REST_DURATION_MS),),
    )
    engine.rule_engine = RuleEngine({PK.ROOK: RookRule()})

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    legal_moves = engine.get_legal_moves(Position(0, 1))

    assert Position(0, 2) in legal_moves
    assert engine.is_piece_in_cooldown(piece.id) is True


def square(name: str) -> Position:
    file_index = ord(name[0]) - ord("a")
    rank_index = int(name[1]) - 1
    return Position(rank_index, file_index)


def _build_basic_engine(state, validation=None):
    rule_engine = FakeRuleEngine(
        validation if validation is not None else MoveValidation(True, "ok")
    )
    return build_engine_context(
        state,
        rule_engine,
        motion_factory=FakeMotionFactory(),
        config_repository=FakeConfigRepository(),
        state_timer=FakeStateTimer(),
        state_transition_resolver=FakeStateTransitionResolver(),
    )


def create_crossing_engine():
    board = Board(8, 8)
    rook = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("e1"),
    )
    queen = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.QUEEN,
        cell=square("a4"),
    )
    board.add_piece(rook)
    board.add_piece(queen)
    state = GameState(board)

    context = _build_basic_engine(state)
    return context.engine, state, rook, queen


CELL_MS = MovementDurationCalculator.MOVE_DURATION_PER_CELL_MS


def create_chase_engine(pursuer_id=1, escaper_id=2):
    board = Board(8, 8)
    pursuer = Piece(
        id=pursuer_id,
        color=Color.WHITE,
        kind=PieceKind.QUEEN,
        cell=square("a1"),
    )
    escaper = Piece(
        id=escaper_id,
        color=Color.BLACK,
        kind=PieceKind.PAWN,
        cell=square("a4"),
    )
    board.add_piece(pursuer)
    board.add_piece(escaper)
    state = GameState(board)

    context = _build_basic_engine(state)
    return context.engine, state, pursuer, escaper


def test_mid_flight_enemy_capture_removes_victim_and_cancels_motion():
    engine, state, rook, queen = create_crossing_engine()

    engine.realtime_arbiter.start_motion(
        Motion(1, square("e1"), square("e8"), duration_ms=7000)
    )
    engine.realtime_arbiter.start_motion(
        Motion(2, square("a4"), square("h4"), duration_ms=7000)
    )

    captured = engine.wait(5000)

    assert captured == [rook]
    assert state.board.get_piece_by_id(1) is None
    assert engine.realtime_arbiter.has_motion(1) is False
    assert engine.realtime_arbiter.has_motion(2) is True


def test_mid_flight_victim_never_reaches_target():
    engine, state, rook, queen = create_crossing_engine()

    engine.realtime_arbiter.start_motion(
        Motion(1, square("e1"), square("e8"), duration_ms=7000)
    )
    engine.realtime_arbiter.start_motion(
        Motion(2, square("a4"), square("h4"), duration_ms=7000)
    )

    engine.wait(5000)
    engine.wait(3000)

    assert state.board.get_piece_by_id(1) is None
    assert state.board.get_piece_by_position(square("e8")) is None
    assert state.board.get_piece_by_id(2) is not None


def test_mid_flight_king_capture_sets_game_over():
    board = Board(8, 8)
    attacker = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("e1"),
    )
    king = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.KING,
        cell=square("d4"),
    )
    board.add_piece(attacker)
    board.add_piece(king)
    state = GameState(board)

    engine = _build_basic_engine(state).engine

    engine.realtime_arbiter.start_motion(
        Motion(1, square("e1"), square("e8"), duration_ms=7000)
    )
    engine.realtime_arbiter.start_motion(
        Motion(2, square("d4"), square("h4"), duration_ms=4000)
    )

    captured = engine.wait(5000)

    assert captured == [king]
    assert state.game_over is True
    assert engine.realtime_arbiter.has_motion(2) is False


def test_standing_enemy_capture_regression_after_event_driven_wait():
    engine, state, _ = create_engine(MoveValidation(True, "ok"))

    enemy = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.ROOK,
        cell=Position(0, 3),
    )
    state.board.add_piece(enemy)

    engine.request_move(Position(0, 0), Position(0, 3))
    captured = engine.wait(1000)

    assert captured == [enemy]
    assert state.board.get_piece_by_position(Position(0, 3)).id == 1
    assert state.board.get_piece_by_id(2) is None


def test_other_piece_can_move_while_piece_is_in_cooldown(tmp_path):
    write_piece_defaults(tmp_path)
    write_state_config(tmp_path, PIECE_CODE, "idle", "idle", speed=0.0)
    write_state_config(tmp_path, PIECE_CODE, "move", "long_rest")
    write_state_config(
        tmp_path,
        PIECE_CODE,
        "long_rest",
        "idle",
        speed=0.0,
        duration_ms=LONG_REST_DURATION_MS,
    )
    write_state_config(
        tmp_path,
        PIECE_CODE,
        "jump",
        "short_rest",
        speed=3.0,
        duration_ms=500,
    )

    board = Board(8, 8)
    resting_piece = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0),
    )
    free_piece = Piece(
        id=2,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(2, 0),
    )
    board.add_piece(resting_piece)
    board.add_piece(free_piece)
    state = GameState(board)

    repository = PieceConfigRepository(tmp_path)
    resolver = StateTransitionResolver(repository)
    context = build_engine_context(
        state,
        FakeRuleEngine(MV(True, "ok")),
        motion_factory=FakeMotionFactory(),
        config_repository=repository,
        state_timer=StateTimer(),
        state_transition_resolver=resolver,
        assets_root=tmp_path,
    )
    engine = context.engine

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    result = engine.request_move(Position(2, 0), Position(2, 1))

    assert result.is_accepted is True


def create_friendly_convergence_engine():
    board = Board(8, 8)
    first = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0),
    )
    second = Piece(
        id=2,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 5),
    )
    board.add_piece(first)
    board.add_piece(second)
    state = GameState(board)

    context = _build_basic_engine(state)
    return context.engine, state, first, second


def test_friendly_convergence_keeps_first_piece_at_target():
    engine, state, first, second = create_friendly_convergence_engine()

    target = Position(0, 3)
    engine.realtime_arbiter.start_motion(
        Motion(1, Position(0, 0), target, duration_ms=500)
    )
    engine.realtime_arbiter.start_motion(
        Motion(2, Position(0, 5), target, duration_ms=1000)
    )

    captured = engine.wait(1000)

    assert captured == []
    assert state.board.get_piece_by_id(first.id) is not None
    assert state.board.get_piece_by_position(target).id == first.id
    assert state.board.get_piece_by_id(second.id) is not None
    assert state.board.get_piece_by_position(Position(0, 4)).id == second.id


def test_friendly_arrival_bounce_one_cell():
    board = Board(8, 8)
    mover = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("a1"),
    )
    blocker = Piece(
        id=2,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("a4"),
    )
    board.add_piece(mover)
    board.add_piece(blocker)
    state = GameState(board)

    engine = _build_basic_engine(state).engine

    engine.realtime_arbiter.start_motion(
        Motion(1, square("a1"), square("a4"), duration_ms=3000)
    )

    captured = engine.wait(3000)

    assert captured == []
    assert state.board.get_piece_by_position(square("a3")).id == 1
    assert state.board.get_piece_by_position(square("a4")).id == 2
    assert state.board.get_piece_by_position(square("a1")) is None


def test_friendly_arrival_bounce_skips_friendly_chain():
    board = Board(8, 8)
    mover = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("a1"),
    )
    friendly_four = Piece(
        id=2,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("a4"),
    )
    friendly_five = Piece(
        id=3,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("a5"),
    )
    board.add_piece(mover)
    board.add_piece(friendly_four)
    board.add_piece(friendly_five)
    state = GameState(board)

    engine = _build_basic_engine(state).engine

    engine.realtime_arbiter.start_motion(
        Motion(1, square("a1"), square("a5"), duration_ms=4000)
    )

    captured = engine.wait(4000)

    assert captured == []
    assert state.board.get_piece_by_position(square("a3")).id == 1


def test_friendly_arrival_bounce_captures_enemy_on_path():
    board = Board(8, 8)
    mover = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("a1"),
    )
    enemy = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.ROOK,
        cell=square("a4"),
    )
    friendly = Piece(
        id=3,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("a5"),
    )
    board.add_piece(mover)
    board.add_piece(enemy)
    board.add_piece(friendly)
    state = GameState(board)

    engine = _build_basic_engine(state).engine

    engine.realtime_arbiter.start_motion(
        Motion(1, square("a1"), square("a5"), duration_ms=4000)
    )

    captured = engine.wait(4000)

    assert captured == [enemy]
    assert state.board.get_piece_by_position(square("a4")).id == 1
    assert state.board.get_piece_by_id(2) is None


def test_motion_completion_sets_has_moved():
    board = Board(8, 8)
    pawn = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.PAWN,
        cell=Position(6, 3),
    )
    board.add_piece(pawn)
    state = GameState(board)

    engine = _build_basic_engine(state).engine

    engine.realtime_arbiter.start_motion(
        Motion(1, Position(6, 3), Position(5, 3), duration_ms=1000)
    )

    assert pawn.has_moved is False

    engine.wait(1000)

    assert pawn.has_moved is True


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


def create_promotion_engine(state, pawn, handler, state_transition_resolver=None):
    return build_engine_context(
        state,
        FakeRuleEngine(MoveValidation(True, "ok")),
        motion_factory=FakeMotionFactory(),
        config_repository=FakeConfigRepository(),
        state_timer=FakeStateTimer(),
        state_transition_resolver=state_transition_resolver or FakeStateTransitionResolver(),
        pawn_end_handler=handler,
    )


def land_white_pawn_on_promotion_rank(state_transition_resolver=None):
    board = Board(8, 8)
    pawn = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.PAWN,
        cell=Position(1, 3),
    )
    board.add_piece(pawn)
    state = GameState(board)
    transition_resolver = (
        state_transition_resolver or TrackingStateTransitionResolver()
    )
    context = create_promotion_engine(
        state,
        pawn,
        ChessPawnEndHandler(),
        transition_resolver,
    )
    context.engine.realtime_arbiter.start_motion(
        Motion(1, Position(1, 3), Position(0, 3), duration_ms=1000)
    )
    context.engine.wait(1000)
    return context.engine, state, pawn, transition_resolver


def board_with_pending_promotion():
    board = Board(8, 8)
    pawn = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.PAWN,
        cell=Position(0, 3),
    )
    rook = Piece(
        id=2,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(4, 4),
    )
    board.add_piece(pawn)
    board.add_piece(rook)
    state = GameState(board)
    state.pending_pawn_promotion = PendingPawnPromotion(
        piece_id=pawn.id,
        allowed_kinds=ChessPawnEndHandler.PROMOTION_KINDS,
    )
    context = create_promotion_engine(state, pawn, ChessPawnEndHandler())
    return context.engine, state, pawn, rook


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


def test_chase_escaping_piece_completes_before_pursuer_arrival():
    engine, state, pursuer, escaper = create_chase_engine()

    engine.realtime_arbiter.start_motion(
        Motion(
            pursuer.id,
            square("a1"),
            square("a4"),
            duration_ms=3 * CELL_MS,
        )
    )
    engine.realtime_arbiter.start_motion(
        Motion(
            escaper.id,
            square("a4"),
            square("a5"),
            duration_ms=CELL_MS,
        )
    )

    captured = engine.wait(3 * CELL_MS)

    assert captured == []
    assert state.board.get_piece_by_id(escaper.id) is not None
    assert state.board.get_piece_by_position(square("a5")).id == escaper.id
    assert state.board.get_piece_by_position(square("a4")).id == pursuer.id


def test_chase_pursuer_captures_when_arriving_before_escape_completes():
    engine, state, pursuer, escaper = create_chase_engine()

    engine.realtime_arbiter.start_motion(
        Motion(
            pursuer.id,
            square("a1"),
            square("a4"),
            duration_ms=3 * CELL_MS,
        )
    )
    engine.wait(2500)
    engine.realtime_arbiter.start_motion(
        Motion(
            escaper.id,
            square("a4"),
            square("a5"),
            duration_ms=CELL_MS,
        )
    )

    captured = engine.wait(500)

    assert captured == [escaper]
    assert state.board.get_piece_by_id(escaper.id) is None
    assert state.board.get_piece_by_position(square("a4")).id == pursuer.id
    assert state.board.get_piece_by_position(square("a5")) is None


def test_chase_same_time_completion_uses_piece_id_priority():
    engine, state, pursuer, escaper = create_chase_engine()

    engine.realtime_arbiter.start_motion(
        Motion(
            pursuer.id,
            square("a1"),
            square("a4"),
            duration_ms=3 * CELL_MS,
        )
    )
    engine.wait(2 * CELL_MS)
    engine.realtime_arbiter.start_motion(
        Motion(
            escaper.id,
            square("a4"),
            square("a5"),
            duration_ms=CELL_MS,
        )
    )

    captured = engine.wait(CELL_MS)

    assert captured == [escaper]
    assert state.board.get_piece_by_id(escaper.id) is None
    assert state.board.get_piece_by_position(square("a4")).id == pursuer.id


def test_occupied_cells_keeps_single_entry_per_piece():
    from kungfu_chess.engine.collision_decisions import STATIONARY_ENTRY_TIME_MS

    occupied_cells = {}
    MotionCompletionService._set_piece_occupied_cell(
        occupied_cells,
        1,
        Color.WHITE,
        Position(0, 0),
        STATIONARY_ENTRY_TIME_MS,
    )
    MotionCompletionService._set_piece_occupied_cell(
        occupied_cells,
        1,
        Color.WHITE,
        Position(0, 1),
        1000,
    )
    MotionCompletionService._set_piece_occupied_cell(
        occupied_cells,
        1,
        Color.WHITE,
        Position(0, 2),
        2000,
    )

    piece_cells = [
        cell for cell, occupant in occupied_cells.items() if occupant.piece_id == 1
    ]

    assert len(piece_cells) == 1
    assert piece_cells[0] == Position(0, 2)


def test_occupied_cells_invariant_during_mid_path_wait():
    from kungfu_chess.engine.collision_decisions import CellEntryEvent

    engine, state, rook, queen = create_crossing_engine()
    simulation_service = engine._simulation_service

    engine.realtime_arbiter.start_motion(
        Motion(1, square("e1"), square("e8"), duration_ms=7000)
    )
    engine.realtime_arbiter.start_motion(
        Motion(2, square("a4"), square("h4"), duration_ms=7000)
    )

    occupied_cells = CompleteSimulationService._build_initial_occupied_cells(
        state.board,
        engine.realtime_arbiter.active_motions(),
    )

    events = simulation_service.collision_resolver.schedule_timeline_events(
        state.board,
        engine.realtime_arbiter.active_motions(),
        within_ms=3500,
    )

    captured_pieces = []
    elapsed = 0
    for event in events:
        step = event.time_from_wait_start_ms - elapsed
        if step > 0:
            engine.realtime_arbiter.advance_time(step)
            elapsed = event.time_from_wait_start_ms

        if isinstance(event, CellEntryEvent):
            outcome = simulation_service.collision_resolver.resolve_entry_event(
                event,
                state.board,
                occupied_cells,
            )
            simulation_service._apply_entry_outcome(
                outcome,
                event,
                occupied_cells,
                captured_pieces,
            )

    for piece_id in (1, 2):
        piece_cells = [
            cell
            for cell, occupant in occupied_cells.items()
            if occupant.piece_id == piece_id
        ]
        assert len(piece_cells) == 1


def test_head_on_same_file_captures_one_enemy():
    board = Board(8, 8)
    white_rook = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("e1"),
    )
    black_rook = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.ROOK,
        cell=square("e8"),
    )
    board.add_piece(white_rook)
    board.add_piece(black_rook)
    state = GameState(board)

    engine = _build_basic_engine(state).engine

    engine.realtime_arbiter.start_motion(
        Motion(1, square("e1"), square("e8"), duration_ms=7000)
    )
    engine.realtime_arbiter.start_motion(
        Motion(2, square("e8"), square("e1"), duration_ms=7000)
    )

    captured = engine.wait(5000)

    assert len(captured) == 1
    assert captured[0].id in {1, 2}
    assert state.board.get_piece_by_id(captured[0].id) is None
    assert state.board.get_piece_by_id(3 - captured[0].id) is not None