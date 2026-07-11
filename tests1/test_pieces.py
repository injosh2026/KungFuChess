import pytest

from helpers import make_board
from pieces import get_route_type, is_valid_move


def test_is_valid_move_same_square_returns_false():
    board = make_board(4, 4)
    assert is_valid_move(board, "wK", (0, 0), (0, 0)) is False


def test_is_valid_move_unknown_piece_type_returns_false():
    board = make_board(4, 4)
    assert is_valid_move(board, "wX", (0, 0), (0, 1)) is False


@pytest.mark.parametrize(
    "piece, start, end",
    [
        ("wK", (0, 0), (0, 1)),
        ("wR", (0, 0), (0, 3)),
        ("wB", (0, 0), (3, 3)),
        ("wQ", (0, 0), (3, 0)),
        ("wN", (0, 0), (2, 1)),
        ("wP", (3, 0), (2, 0)),
    ],
)
def test_is_valid_move_valid_moves_by_piece_type(piece, start, end):
    board = make_board(4, 4)
    assert is_valid_move(board, piece, start, end) is True


@pytest.mark.parametrize(
    "piece, start, end",
    [
        ("wK", (0, 0), (0, 2)),
        ("wR", (0, 0), (2, 2)),
        ("wB", (0, 0), (2, 0)),
        ("wQ", (0, 0), (2, 1)),
        ("wN", (0, 0), (1, 1)),
        ("wP", (3, 0), (2, 1)),
    ],
)
def test_is_valid_move_invalid_moves_by_piece_type(piece, start, end):
    board = make_board(4, 4)
    assert is_valid_move(board, piece, start, end) is False


def test_is_valid_move_rook_blocked_path():
    board = make_board(4, 4)
    board[0][1] = "wR"
    assert is_valid_move(board, "wR", (0, 0), (0, 3)) is False


@pytest.mark.parametrize(
    "start, end, expected",
    [
        ((0, 0), (0, 3), "horizontal"),
        ((0, 0), (3, 0), "vertical"),
        ((0, 0), (3, 3), "diagonal"),
        ((0, 0), (0, 1), "horizontal"),
        ((0, 0), (1, 0), "vertical"),
        ((0, 0), (1, 1), "diagonal"),
        ((0, 0), (0, 0), "horizontal"),
    ],
)
def test_get_route_type(start, end, expected):
    assert get_route_type(start, end) == expected
