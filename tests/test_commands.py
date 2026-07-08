import copy

import pytest

from commands import process_commands
from helpers import make_board


@pytest.mark.parametrize("line", ["", "   "])
def test_process_commands_skips_empty_lines(line):
    board = make_board(4, 4)
    board[0][0] = "wK"
    expected = copy.deepcopy(board)

    process_commands([line], 0, board)

    assert board == expected


def test_process_commands_ignores_unknown_command():
    board = make_board(4, 4)
    board[0][0] = "wK"
    expected = copy.deepcopy(board)

    process_commands(["foo bar"], 0, board)

    assert board == expected


def test_process_commands_print_board(capsys):
    board = make_board(2, 2)
    board[0][0] = "wK"
    board[0][1] = "bP"

    process_commands(["print board"], 0, board)

    assert capsys.readouterr().out == "wK bP\n. .\n"


def test_process_commands_print_something_else_does_not_print(capsys):
    board = make_board(2, 2)

    process_commands(["print something"], 0, board)

    assert capsys.readouterr().out == ""


def test_process_commands_click_in_bounds_selects_and_moves_piece():
    board = make_board(4, 4)
    board[0][0] = "wK"

    process_commands(
        [
            "click 0 0",
            "click 100 0",
            "wait 1000",
        ],
        0,
        board,
    )

    assert board[0][0] == "."
    assert board[0][1] == "wK"


def test_process_commands_click_converts_coordinates_with_integer_division():
    board = make_board(4, 4)
    board[1][1] = "wK"

    process_commands(
        [
            "click 100 100",
            "click 200 200",
            "wait 1000",
        ],
        0,
        board,
    )

    assert board[1][1] == "."
    assert board[2][2] == "wK"


@pytest.mark.parametrize(
    "command",
    [
        "click 0 -100",
        "click -100 0",
        "click 1000 0",
        "click 0 1000",
    ],
)
def test_process_commands_click_out_of_bounds_does_not_change_board(command):
    board = make_board(4, 4)
    board[0][0] = "wK"
    expected = copy.deepcopy(board)

    process_commands([command], 0, board)

    assert board == expected


def test_process_commands_wait_completes_pending_move_after_enough_time():
    board = make_board(4, 4)
    board[0][0] = "wK"

    process_commands(
        [
            "click 0 0",
            "click 100 0",
            "wait 1000",
        ],
        0,
        board,
    )

    assert board[0][0] == "."
    assert board[0][1] == "wK"


def test_process_commands_wait_accumulates_time_across_multiple_commands():
    board = make_board(4, 4)
    board[0][0] = "wK"

    process_commands(
        [
            "click 0 0",
            "click 100 0",
            "wait 500",
            "wait 500",
        ],
        0,
        board,
    )

    assert board[0][0] == "."
    assert board[0][1] == "wK"


def test_process_commands_jump_in_bounds_does_not_crash():
    board = make_board(4, 4)
    board[1][1] = "wK"
    expected = copy.deepcopy(board)

    process_commands(["jump 100 100"], 0, board)

    assert board == expected


@pytest.mark.parametrize(
    "command",
    [
        "jump 0 -100",
        "jump -100 0",
        "jump 1000 0",
        "jump 0 1000",
    ],
)
def test_process_commands_jump_out_of_bounds_does_not_change_board(command):
    board = make_board(4, 4)
    board[1][1] = "wK"
    expected = copy.deepcopy(board)

    process_commands([command], 0, board)

    assert board == expected


def test_process_commands_sequence_click_wait_print(capsys):
    board = make_board(4, 4)
    board[0][0] = "wK"

    process_commands(
        [
            "click 0 0",
            "click 100 0",
            "wait 1000",
            "print board",
        ],
        0,
        board,
    )

    assert board[0][0] == "."
    assert board[0][1] == "wK"
    assert ". wK" in capsys.readouterr().out


def test_process_commands_respects_start_index():
    board = make_board(4, 4)
    board[0][0] = "wK"

    process_commands(
        [
            "click 0 0",
            "click 100 0",
            "wait 1000",
        ],
        2,
        board,
    )

    assert board[0][0] == "wK"
    assert board[0][1] == "."
