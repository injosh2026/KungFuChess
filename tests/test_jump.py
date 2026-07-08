import pytest

from helpers import make_board, make_game_state, make_move
from jump import handle_jump


def test_handle_jump_adds_jump_for_stationary_piece():
    board = make_board(4, 4)
    board[1][1] = "wN"
    pending_jumps = []

    handle_jump(board, 1, 1, pending_jumps, [], 0, make_game_state())

    assert len(pending_jumps) == 1
    assert pending_jumps[0]["piece"] == "wN"
    assert pending_jumps[0]["position"] == (1, 1)
    assert pending_jumps[0]["end_time"] == 1000


def test_handle_jump_sets_end_time_from_game_time():
    board = make_board(4, 4)
    board[2][0] = "wR"
    pending_jumps = []

    handle_jump(board, 2, 0, pending_jumps, [], 500, make_game_state())

    assert pending_jumps[0]["end_time"] == 1500


@pytest.mark.parametrize("piece", ["bK", "bP"])
def test_handle_jump_works_for_black_pieces(piece):
    board = make_board(4, 4)
    board[0][0] = piece
    pending_jumps = []

    handle_jump(board, 0, 0, pending_jumps, [], 0, make_game_state())

    assert pending_jumps[0]["piece"] == piece
    assert pending_jumps[0]["position"] == (0, 0)


def test_handle_jump_appends_to_existing_pending_jumps():
    board = make_board(4, 4)
    board[1][1] = "wN"
    existing_jump = {
        "piece": "bB",
        "position": (3, 3),
        "end_time": 2000,
    }
    pending_jumps = [existing_jump]

    handle_jump(board, 1, 1, pending_jumps, [], 0, make_game_state())

    assert len(pending_jumps) == 2
    assert pending_jumps[0] == existing_jump
    assert pending_jumps[1]["piece"] == "wN"
    assert pending_jumps[1]["position"] == (1, 1)


def test_handle_jump_does_nothing_when_game_is_over():
    board = make_board(4, 4)
    board[1][1] = "wN"
    pending_jumps = []

    handle_jump(board, 1, 1, pending_jumps, [], 0, make_game_state(game_over=True))

    assert pending_jumps == []


def test_handle_jump_does_nothing_on_empty_square():
    board = make_board(4, 4)
    pending_jumps = []

    handle_jump(board, 0, 0, pending_jumps, [], 0, make_game_state())

    assert pending_jumps == []


def test_handle_jump_does_nothing_when_piece_is_moving():
    board = make_board(4, 4)
    board[0][0] = "wK"
    pending_moves = [make_move("wK", (0, 0), (0, 1))]
    pending_jumps = []

    handle_jump(board, 0, 0, pending_jumps, pending_moves, 0, make_game_state())

    assert pending_jumps == []
