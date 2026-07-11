import pytest

from kungfu_chess.engine.move_result import MoveResult


def test_accepted_move_result():

    result = MoveResult(is_accepted=True, reason="ok")

    assert result.is_accepted is True
    assert result.reason == "ok"


def test_rejected_move_result():

    result = MoveResult(is_accepted=False, reason="game_over")

    assert result.is_accepted is False
    assert result.reason == "game_over"


def test_move_result_is_immutable():

    result = MoveResult(is_accepted=True, reason="ok")

    with pytest.raises(Exception):
        result.reason = "changed"
