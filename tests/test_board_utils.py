import pytest

from board_utils import is_path_clear
from helpers import make_board

def test_is_path_clear_horizontal_right():
    board = make_board(4, 4)
    assert is_path_clear(board, (0, 0), (0, 3)) is True


def test_is_path_clear_horizontal_left():
    board = make_board(4, 4)
    assert is_path_clear(board, (0, 3), (0, 0)) is True


def test_is_path_clear_vertical_down():
    board = make_board(4, 4)
    assert is_path_clear(board, (0, 0), (3, 0)) is True


def test_is_path_clear_vertical_up():
    board = make_board(4, 4)
    assert is_path_clear(board, (3, 0), (0, 0)) is True


def test_is_path_clear_diagonal_down_right():
    board = make_board(4, 4)
    assert is_path_clear(board, (0, 0), (3, 3)) is True


def test_is_path_clear_diagonal_up_left():
    board = make_board(4, 4)
    assert is_path_clear(board, (3, 3), (0, 0)) is True


@pytest.mark.parametrize(
    "start, end",
    [
        ((0, 0), (0, 1)),
        ((0, 0), (1, 0)),
        ((0, 0), (1, 1)),
    ],
)
def test_is_path_clear_adjacent_squares_have_no_squares_between(start, end):
    board = make_board(4, 4)
    assert is_path_clear(board, start, end) is True


@pytest.mark.parametrize(
    "start, end, blocked_pos, blocker",
    [
        ((0, 0), (0, 3), (0, 1), "wR"),
        ((0, 0), (3, 0), (1, 0), "bP"),
        ((0, 0), (3, 3), (1, 1), "wK"),
    ],
)
def test_is_path_clear_returns_false_when_path_is_blocked(
    start, end, blocked_pos, blocker
):
    board = make_board(4, 4)
    row, col = blocked_pos
    board[row][col] = blocker
    assert is_path_clear(board, start, end) is False


def test_is_path_clear_ignores_piece_at_start():
    board = make_board(4, 4)
    board[0][0] = "wR"
    assert is_path_clear(board, (0, 0), (0, 3)) is True


def test_is_path_clear_ignores_piece_at_end():
    board = make_board(4, 4)
    board[0][3] = "bK"
    assert is_path_clear(board, (0, 0), (0, 3)) is True
