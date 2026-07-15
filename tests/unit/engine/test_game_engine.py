from kungfu_chess.config.piece_config_repository import PieceConfigRepository
from kungfu_chess.config.state_config import GraphicsConfig, PhysicsConfig, StateConfig
from kungfu_chess.engine.game_engine import GameEngine, PIECE_IN_COOLDOWN, PIECE_IN_MOTION
from kungfu_chess.engine.state_transition_resolver import StateTransitionResolver
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter
from kungfu_chess.realtime.state_timer import StateTimer
from kungfu_chess.rules.move_validation import MoveValidation


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


class FakeConfigRepository:

    def __init__(self, move_command_state="move"):
        self.move_command_state = move_command_state

    def get_move_command_state(self, piece_code):
        return self.move_command_state

    def load_state(self, piece_code, state_name):
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

    engine = GameEngine(
        state,
        rule_engine,
        RealTimeArbiter(),
        FakeMotionFactory(),
        FakeStateTransitionResolver(),
        FakeConfigRepository(),
        FakeStateTimer(),
    )

    return engine, state, rule_engine


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

    engine = GameEngine(
        state,
        FakeRuleEngine(MoveValidation(True, "ok")),
        RealTimeArbiter(),
        FakeMotionFactory(),
        FakeStateTransitionResolver(),
        FakeConfigRepository(),
        FakeStateTimer(),
    )

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

    engine = GameEngine(
        state,
        FakeRuleEngine(MoveValidation(True, "ok")),
        RealTimeArbiter(),
        FakeMotionFactory(),
        FakeStateTransitionResolver(),
        FakeConfigRepository(),
        FakeStateTimer(),
    )

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

    engine = GameEngine(
        state,
        FakeRuleEngine(MoveValidation(True, "ok")),
        arbiter,
        FakeMotionFactory(),
        FakeStateTransitionResolver(),
        FakeConfigRepository(),
        FakeStateTimer(),
    )

    engine.wait(700)

    assert arbiter.called_with == 700


import json
from pathlib import Path

from kungfu_chess.rules.move_validation import MoveValidation as MV

PIECE_CODE = "RW"


def write_piece_defaults(root: Path) -> None:
    defaults = {"initial_state": "idle", "move_command_state": "move"}
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

    engine = GameEngine(
        state,
        FakeRuleEngine(MV(True, "ok")),
        RealTimeArbiter(),
        FakeMotionFactory(),
        resolver,
        repository,
        StateTimer(),
    )
    return engine, piece


def test_completed_move_transitions_to_idle_from_config(tmp_path):
    engine, piece = create_configured_engine(tmp_path, "idle")

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    assert piece.state == "idle"


def test_completed_move_transitions_to_long_rest_from_config(tmp_path):
    engine, piece = create_configured_engine(
        tmp_path,
        "long_rest",
        extra_states=(("long_rest", "idle", 0.0, 1000),),
    )

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    assert piece.state == "long_rest"


def test_long_rest_with_duration_transitions_to_idle_after_timer(tmp_path):
    engine, piece = create_configured_engine(
        tmp_path,
        "long_rest",
        extra_states=(("long_rest", "idle", 0.0, 1000),),
    )

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    assert piece.state == "long_rest"

    engine.wait(500)
    assert piece.state == "long_rest"

    engine.wait(500)
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
        extra_states=(("long_rest", "idle", 0.0, 1000),),
    )

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    assert engine.state_timer_progress(piece.id) == 0.0

    engine.wait(250)
    assert engine.state_timer_progress(piece.id) == 0.25

    engine.wait(750)
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
    engine = GameEngine(
        state,
        FakeRuleEngine(MV(True, "ok")),
        RealTimeArbiter(),
        FakeMotionFactory(),
        resolver,
        repository,
        StateTimer(),
    )

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
        extra_states=(("long_rest", "idle", 0.0, 1000),),
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
        extra_states=(("long_rest", "idle", 0.0, 1000),),
    )

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)
    engine.wait(1000)

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
        extra_states=(("long_rest", "idle", 0.0, 1000),),
    )
    engine.rule_engine = RuleEngine({PK.ROOK: RookRule()})

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    legal_moves = engine.get_legal_moves(Position(0, 1))

    assert Position(0, 2) in legal_moves
    assert engine.is_piece_in_cooldown(piece.id) is True


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
        duration_ms=1000,
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
    engine = GameEngine(
        state,
        FakeRuleEngine(MV(True, "ok")),
        RealTimeArbiter(),
        FakeMotionFactory(),
        resolver,
        repository,
        StateTimer(),
    )

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    result = engine.request_move(Position(2, 0), Position(2, 1))

    assert result.is_accepted is True