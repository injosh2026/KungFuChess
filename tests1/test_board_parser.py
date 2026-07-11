import pytest

from board_parser import parse_board, validate_board
from helpers import make_lines


def test_parse_board_returns_board_and_commands_index():
    lines = make_lines(["wK ."])

    board, commands_index = parse_board(lines)

    assert board == [["wK", "."]]
    assert commands_index == 2
    assert lines[commands_index] == "Commands:"


def test_parse_board_parses_multiple_rows():
    lines = make_lines([". wK .", ". . bP"])

    board, commands_index = parse_board(lines)

    assert board == [[".", "wK", "."], [".", ".", "bP"]]
    assert commands_index == 3


def test_parse_board_returns_none_on_row_width_mismatch():
    lines = make_lines([". wK", ". . ."])

    board, commands_index = parse_board(lines)

    assert board is None
    assert commands_index is None


def test_parse_board_returns_none_on_unknown_token():
    lines = make_lines(["wX ."])

    board, commands_index = parse_board(lines)

    assert board is None
    assert commands_index is None


def test_validate_board_returns_true_for_valid_board():
    board = [[".", "wK"], [".", "bP"]]

    assert validate_board(board) is True


@pytest.mark.parametrize(
    "board",
    [
        [[".", "wK"], ["."]],
        [[".", "wK"], [".", ".", "."]],
    ],
)
def test_validate_board_row_width_mismatch(board, capsys):
    assert validate_board(board) is False
    assert capsys.readouterr().out == "ERROR ROW_WIDTH_MISMATCH\n"


@pytest.mark.parametrize(
    "token",
    ["wX", "..", "WK"],
)
def test_validate_board_unknown_token(token, capsys):
    board = [[".", token]]

    assert validate_board(board) is False
    assert capsys.readouterr().out == "ERROR UNKNOWN_TOKEN\n"


def test_validate_board_no_output_on_success(capsys):
    board = [[".", "wK"], [".", "bP"]]

    assert validate_board(board) is True
    assert capsys.readouterr().out == ""
