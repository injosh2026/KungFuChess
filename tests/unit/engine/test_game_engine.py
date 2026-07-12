from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter
from kungfu_chess.rules.move_validation import MoveValidation


class FakeRuleEngine:

    def __init__(self, validation):
        self.validation = validation
        self.called = False

    def validate_move(self, board, source, destination):
        self.called = True
        return self.validation


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
        RealTimeArbiter()
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


def test_cannot_start_move_when_motion_active():

    engine, _, rule_engine = create_engine(MoveValidation(True, "ok"))

    engine.realtime_arbiter.start_motion(create_motion())

    result = engine.request_move(Position(0, 0), Position(0, 1))

    assert result.is_accepted is False
    assert result.reason == "motion_in_progress"

    assert rule_engine.called is False


def test_valid_move_without_source_piece_raises_error():

    engine, state, _ = create_engine(MoveValidation(True, "ok"))

    state.board.remove_piece(Position(0,0))

    try:
        engine.request_move(Position(0,0), Position(0,1))
        assert False
    except RuntimeError as e:
        assert str(e) == "Validated move without source piece"


def test_wait_advances_active_motion_time():

    engine, _, _ = create_engine(MoveValidation(True, "ok"))

    motion = create_motion()

    engine.realtime_arbiter.start_motion(motion)

    engine.wait(500)

    assert engine.realtime_arbiter.active_motion is not None
    assert engine.realtime_arbiter.active_motion.elapsed_ms == 500