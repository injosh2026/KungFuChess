from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.position import Position
from kungfu_chess.rules.move_validation import MoveValidation


class FakeRuleEngine:

    def __init__(self, validation):
        self.validation = validation
        self.called = False

    def validate_move(
        self,
        board,
        source,
        destination
    ):
        self.called = True
        return self.validation


def create_engine(validation):

    board = Board(8, 8)

    state = GameState(board)

    rule_engine = FakeRuleEngine(validation)

    engine = GameEngine(
        state,
        rule_engine
    )

    return engine, state, rule_engine


def test_game_over_rejects_move():

    engine, state, rule_engine = create_engine(
        MoveValidation(
            True,
            "ok"
        )
    )

    state.game_over = True

    result = engine.request_move(
        Position(0, 0),
        Position(0, 1)
    )

    assert result.is_accepted is False
    assert result.reason == "game_over"

    assert rule_engine.called is False


def test_valid_move_returns_ok():

    engine, _, rule_engine = create_engine(
        MoveValidation(
            True,
            "ok"
        )
    )

    result = engine.request_move(
        Position(0, 0),
        Position(0, 1)
    )

    assert result.is_accepted is True
    assert result.reason == "ok"

    assert rule_engine.called is True


def test_invalid_move_returns_reason():

    engine, _, _ = create_engine(
        MoveValidation(
            False,
            "illegal_piece_move"
        )
    )

    result = engine.request_move(
        Position(0, 0),
        Position(3, 3)
    )

    assert result.is_accepted is False
    assert result.reason == "illegal_piece_move"