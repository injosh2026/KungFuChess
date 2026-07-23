from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.rules.move_validation import MoveValidation
from tests.helpers.engine_fakes import FakeArbiter, FakeConfigRepository, FakeMotionFactory, FakeRuleEngine, FakeStateTimer, FakeStateTransitionResolver
from tests.helpers.engine_test_factory import _build_basic_engine, create_engine
from tests.helpers.engine_wiring import build_engine_context


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

    engine, state, _ = create_engine(MoveValidation(True, "ok"))

    engine.request_move(Position(0, 0), Position(0, 1))

    engine.wait(1000)

    assert state.board.get_piece_by_position(Position(0, 0)) is None

    assert state.board.get_piece_by_position(Position(0, 1)) is not None


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
