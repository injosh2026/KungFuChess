from pathlib import Path

from kungfu_chess.config.piece_config_repository import PieceConfigRepository
from kungfu_chess.engine.state_transition_resolver import StateTransitionResolver
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.state_timer import StateTimer
from tests.helpers.engine_fakes import FakeMotionFactory, FakeRuleEngine
from tests.helpers.engine_test_factory import LONG_REST_DURATION_MS, MOTION_DURATION_MS, create_configured_engine
from tests.helpers.engine_wiring import build_engine_context
from kungfu_chess.rules.move_validation import MoveValidation as MV


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

