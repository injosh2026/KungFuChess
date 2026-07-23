from kungfu_chess.engine.services.jump_service import PIECE_IN_MOTION
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.rules.move_validation import MoveValidation
from tests.helpers.engine_test_factory import create_engine
from tests.unit.engine.test_collision_resolver import create_motion


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
