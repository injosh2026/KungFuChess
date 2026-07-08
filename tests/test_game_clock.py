import pytest

from game_clock import (
    calculate_move_time,
    complete_jumps,
    complete_moves,
    handle_airborne_collision,
    handle_wait,
)
from helpers import make_board, make_game_state, make_jump, make_move


@pytest.mark.parametrize(
    "start, end",
    [
        ((0, 0), (0, 1)),
        ((3, 3), (0, 0)),
        ((1, 2), (4, 5)),
    ],
)
def test_calculate_move_time_always_returns_1000(start, end):
    assert calculate_move_time(start, end) == 1000


def test_handle_wait_returns_updated_game_time():
    board = make_board(4, 4)
    pending_moves = []
    pending_jumps = []
    game_state = make_game_state()

    result = handle_wait(750, 250, board, pending_moves, pending_jumps, game_state)

    assert result == 1000


def test_handle_wait_completes_move_to_empty_square():
    board = make_board(4, 4)
    board[0][0] = "wK"
    pending_moves = [make_move("wK", (0, 0), (0, 1), arrival=1000)]
    pending_jumps = []
    game_state = make_game_state()

    handle_wait(1000, 0, board, pending_moves, pending_jumps, game_state)

    assert board[0][0] == "."
    assert board[0][1] == "wK"
    assert pending_moves == []


def test_handle_wait_does_not_complete_move_before_arrival():
    board = make_board(4, 4)
    board[0][0] = "wK"
    pending_moves = [make_move("wK", (0, 0), (0, 1), arrival=2000)]
    pending_jumps = []
    game_state = make_game_state()

    handle_wait(1000, 0, board, pending_moves, pending_jumps, game_state)

    assert board[0][0] == "wK"
    assert board[0][1] == "."
    assert len(pending_moves) == 1


def test_handle_wait_accumulates_time_across_waits():
    board = make_board(4, 4)
    board[0][0] = "wK"
    pending_moves = [make_move("wK", (0, 0), (0, 1), arrival=1000)]
    pending_jumps = []
    game_state = make_game_state()
    game_time = 0

    game_time = handle_wait(500, game_time, board, pending_moves, pending_jumps, game_state)
    assert board[0][0] == "wK"
    assert game_time == 500

    game_time = handle_wait(500, game_time, board, pending_moves, pending_jumps, game_state)
    assert board[0][0] == "."
    assert board[0][1] == "wK"
    assert game_time == 1000
    assert pending_moves == []


def test_handle_wait_completes_expired_jumps():
    board = make_board(4, 4)
    pending_moves = []
    pending_jumps = [make_jump("wN", (1, 1), end_time=1000)]
    game_state = make_game_state()

    handle_wait(1000, 0, board, pending_moves, pending_jumps, game_state)

    assert pending_jumps == []


def test_complete_moves_captures_non_king_piece():
    board = make_board(4, 4)
    board[0][0] = "wR"
    board[0][1] = "bP"
    pending_moves = [make_move("wR", (0, 0), (0, 1), arrival=1000)]
    pending_jumps = []
    game_state = make_game_state()

    complete_moves(board, pending_moves, pending_jumps, 1000, game_state)

    assert board[0][0] == "."
    assert board[0][1] == "wR"
    assert game_state.game_over is False
    assert pending_moves == []


def test_complete_moves_capture_king_sets_game_over():
    board = make_board(4, 4)
    board[0][0] = "wR"
    board[0][1] = "bK"
    pending_moves = [make_move("wR", (0, 0), (0, 1), arrival=1000)]
    pending_jumps = []
    game_state = make_game_state()

    complete_moves(board, pending_moves, pending_jumps, 1000, game_state)

    assert board[0][1] == "wR"
    assert game_state.game_over is True


def test_complete_moves_promotes_white_pawn_to_queen():
    board = make_board(4, 4)
    board[1][0] = "wP"
    pending_moves = [make_move("wP", (1, 0), (0, 0), arrival=1000)]
    pending_jumps = []
    game_state = make_game_state()

    complete_moves(board, pending_moves, pending_jumps, 1000, game_state)

    assert board[1][0] == "."
    assert board[0][0] == "wQ"


def test_complete_moves_promotes_black_pawn_to_queen():
    board = make_board(4, 4)
    board[2][0] = "bP"
    pending_moves = [make_move("bP", (2, 0), (3, 0), arrival=1000)]
    pending_jumps = []
    game_state = make_game_state()

    complete_moves(board, pending_moves, pending_jumps, 1000, game_state)

    assert board[2][0] == "."
    assert board[3][0] == "bQ"


def test_complete_moves_airborne_collision_clears_start_and_does_not_land():
    board = make_board(4, 4)
    board[0][0] = "wR"
    board[0][1] = "bN"
    move = make_move("wR", (0, 0), (0, 1), arrival=1000)
    jump = make_jump("bN", (0, 1))
    pending_moves = [move]
    pending_jumps = [jump]
    game_state = make_game_state()

    complete_moves(board, pending_moves, pending_jumps, 1000, game_state)

    assert board[0][0] == "."
    assert board[0][1] == "bN"
    assert pending_moves == []
    assert pending_jumps == []


def test_complete_jumps_removes_expired_jump():
    board = make_board(4, 4)
    pending_jumps = [make_jump("wN", (1, 1), end_time=1000)]

    complete_jumps(board, pending_jumps, 1000)

    assert pending_jumps == []


def test_complete_jumps_keeps_active_jump():
    board = make_board(4, 4)
    jump = make_jump("wN", (1, 1), end_time=2000)
    pending_jumps = [jump]

    complete_jumps(board, pending_jumps, 1000)

    assert pending_jumps == [jump]


def test_handle_airborne_collision_returns_enemy_jump_on_destination():
    board = make_board(4, 4)
    move = make_move("wR", (0, 0), (0, 1))
    jump = make_jump("bN", (0, 1))

    result = handle_airborne_collision(board, move, [jump])

    assert result == jump


def test_handle_airborne_collision_ignores_same_color_jump():
    board = make_board(4, 4)
    move = make_move("wR", (0, 0), (0, 1))
    jump = make_jump("wN", (0, 1))

    result = handle_airborne_collision(board, move, [jump])

    assert result is None


def test_handle_airborne_collision_returns_none_when_no_jump_on_destination():
    board = make_board(4, 4)
    move = make_move("wR", (0, 0), (0, 1))
    jump = make_jump("bN", (2, 2))

    result = handle_airborne_collision(board, move, [jump])

    assert result is None
