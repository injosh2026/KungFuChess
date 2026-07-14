import pytest

from kungfu_chess.texttests.script_runner import ScriptRunner
from kungfu_chess.model.board import Board


class FakeGameEngine:

    def __init__(self):
        self.wait_calls = []


    def wait(self, milliseconds):
        self.wait_calls.append(milliseconds)
        return "done"
    

def test_load_board_creates_game():

    runner = ScriptRunner()

    lines = [
        "wK .",
        ". bK"
    ]

    runner.load_board(lines)

    assert isinstance(runner.board, Board)

    assert runner.controller is not None
    assert runner.game_engine is not None


def test_click_is_sent_to_controller():

    runner = ScriptRunner()

    lines = [
        "wR .",
        ". ."
    ]

    runner.load_board(lines)

    runner.handle_click(50, 50)

    assert runner.controller.selected_position.row == 0
    assert runner.controller.selected_position.col == 0


def test_click_without_loaded_game_raises_error():

    runner = ScriptRunner()

    with pytest.raises(
        RuntimeError,
        match="Game is not initialized"
    ):
        runner.handle_click(50, 50)


def test_wait_is_sent_to_game_engine():

    runner = ScriptRunner()

    engine = FakeGameEngine()

    runner.game_engine = engine

    result = runner.wait(1000)

    assert result == "done"

    assert engine.wait_calls == [1000]


def test_wait_without_loaded_game_raises_error():

    runner = ScriptRunner()

    with pytest.raises(
        RuntimeError,
        match="Game is not initialized"
    ):
        runner.wait(1000)


def test_print_board_returns_board_text():

    runner = ScriptRunner()

    lines = [
        "wK .",
        ". bK"
    ]

    runner.load_board(lines)

    output = runner.print_board()

    assert "wK" in output
    assert "bK" in output


def test_print_board_without_loaded_game_raises_error():

    runner = ScriptRunner()

    with pytest.raises(
        RuntimeError,
        match="Game is not initialized"
    ):
        runner.print_board()


def test_run_ignores_empty_lines():

    runner = ScriptRunner()

    result = runner.run([
        "",
        "   ",
        ""
    ])

    assert result == []


def test_run_rejects_unknown_command():

    runner = ScriptRunner()

    with pytest.raises(
        ValueError,
        match="Unknown command: hello"
    ):
        runner.run([
            "hello"
        ])


def test_run_prints_initial_board():

    runner = ScriptRunner()

    output = runner.run([
        "Board",
        "wK .",
        ". bK",
        "",
        "print board",
    ])

    assert output == [
        "wK .\n. bK"
    ]


def test_run_executes_click_command():

    runner = ScriptRunner()

    runner.run([
        "Board",
        "wR .",
        ". .",
        "",
        "click 50 50",
    ])

    assert runner.controller.selected_position.row == 0
    assert runner.controller.selected_position.col == 0


def test_run_executes_wait_command():

    runner = ScriptRunner()

    runner.run([
        "Board",
        "wR .",
        ". .",
        "",
        "wait 1000",
    ])

    assert runner.game_engine is not None