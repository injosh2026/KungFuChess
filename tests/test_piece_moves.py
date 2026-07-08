import pytest

from helpers import make_board
from piece_moves import (
    bishop_move,
    is_pawn_start_row,
    king_move,
    knight_move,
    pawn_move,
    queen_move,
    rook_move,
)


@pytest.mark.parametrize(
    "row_diff, col_diff, expected",
    [
        (1, 0, True),
        (0, 1, True),
        (1, 1, True),
        (2, 0, False),
        (0, 2, False),
        (2, 1, False),
    ],
)
def test_king_move(row_diff, col_diff, expected):
    assert king_move(row_diff, col_diff) is expected


@pytest.mark.parametrize(
    "row_diff, col_diff, expected",
    [
        (2, 1, True),
        (1, 2, True),
        (1, 1, False),
        (2, 2, False),
        (3, 1, False),
    ],
)
def test_knight_move(row_diff, col_diff, expected):
    assert knight_move(row_diff, col_diff) is expected


@pytest.mark.parametrize(
    "piece, start, expected",
    [
        ("wP", (3, 0), True),
        ("bP", (0, 0), True),
        ("wP", (2, 0), False),
        ("bP", (1, 0), False),
    ],
)
def test_is_pawn_start_row(piece, start, expected):
    assert is_pawn_start_row(piece, start) is expected


def test_rook_move_horizontal_clear_path():
    board = make_board(4, 4)
    assert rook_move(board, 0, 3, (0, 0), (0, 3)) is True


def test_rook_move_vertical_clear_path():
    board = make_board(4, 4)
    assert rook_move(board, 3, 0, (0, 0), (3, 0)) is True


def test_rook_move_diagonal_is_invalid():
    board = make_board(4, 4)
    assert rook_move(board, 2, 2, (0, 0), (2, 2)) is False


def test_rook_move_blocked_path():
    board = make_board(4, 4)
    board[0][1] = "wR"
    assert rook_move(board, 0, 3, (0, 0), (0, 3)) is False


def test_bishop_move_diagonal_clear_path():
    board = make_board(4, 4)
    assert bishop_move(board, 3, 3, (0, 0), (3, 3)) is True


def test_bishop_move_non_diagonal_is_invalid():
    board = make_board(4, 4)
    assert bishop_move(board, 2, 0, (0, 0), (2, 0)) is False


def test_bishop_move_blocked_path():
    board = make_board(4, 4)
    board[1][1] = "bB"
    assert bishop_move(board, 3, 3, (0, 0), (3, 3)) is False


def test_queen_move_horizontal_clear_path():
    board = make_board(4, 4)
    assert queen_move(board, 0, 3, (0, 0), (0, 3)) is True


def test_queen_move_vertical_clear_path():
    board = make_board(4, 4)
    assert queen_move(board, 3, 0, (0, 0), (3, 0)) is True


def test_queen_move_diagonal_clear_path():
    board = make_board(4, 4)
    assert queen_move(board, 3, 3, (0, 0), (3, 3)) is True


def test_queen_move_knight_pattern_is_invalid():
    board = make_board(4, 4)
    assert queen_move(board, 2, 1, (0, 0), (2, 1)) is False


def test_queen_move_blocked_path():
    board = make_board(4, 4)
    board[0][1] = "wQ"
    assert queen_move(board, 0, 3, (0, 0), (0, 3)) is False


def test_pawn_move_white_single_step_forward():
    board = make_board(4, 4)
    assert pawn_move(board, "wP", (3, 0), (2, 0)) is True


def test_pawn_move_white_single_step_blocked():
    board = make_board(4, 4)
    board[2][0] = "bP"
    assert pawn_move(board, "wP", (3, 0), (2, 0)) is False


def test_pawn_move_white_double_step_from_start():
    board = make_board(4, 4)
    assert pawn_move(board, "wP", (3, 0), (1, 0)) is True


def test_pawn_move_white_double_step_not_from_start():
    board = make_board(4, 4)
    assert pawn_move(board, "wP", (2, 0), (0, 0)) is False


def test_pawn_move_white_double_step_with_blocked_middle():
    board = make_board(4, 4)
    board[2][0] = "bR"
    assert pawn_move(board, "wP", (3, 0), (1, 0)) is False


def test_pawn_move_white_diagonal_capture():
    board = make_board(4, 4)
    board[2][1] = "bP"
    assert pawn_move(board, "wP", (3, 0), (2, 1)) is True


def test_pawn_move_white_diagonal_capture_empty_square():
    board = make_board(4, 4)
    assert pawn_move(board, "wP", (3, 0), (2, 1)) is False


def test_pawn_move_black_single_step_forward():
    board = make_board(4, 4)
    assert pawn_move(board, "bP", (0, 0), (1, 0)) is True


def test_pawn_move_black_double_step_from_start():
    board = make_board(4, 4)
    assert pawn_move(board, "bP", (0, 0), (2, 0)) is True


def test_pawn_move_black_diagonal_capture():
    board = make_board(4, 4)
    board[1][1] = "wP"
    assert pawn_move(board, "bP", (0, 0), (1, 1)) is True


def test_pawn_move_invalid_backward_move():
    board = make_board(4, 4)
    assert pawn_move(board, "wP", (2, 0), (3, 0)) is False
