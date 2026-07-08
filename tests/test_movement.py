import pytest

from helpers import make_board, make_move, make_session
from movement import can_start_move, handle_click, is_piece_moving, same_color


@pytest.mark.parametrize(
    "piece1, piece2, expected",
    [
        ("wK", "wQ", True),
        ("bP", "bR", True),
        ("wK", "bK", False),
        ("wP", "bP", False),
    ],
)
def test_same_color(piece1, piece2, expected):
    assert same_color(piece1, piece2) is expected


def test_is_piece_moving_returns_true_when_piece_is_in_pending_moves():
    pending_moves = [make_move("wK", (0, 0), (0, 1))]
    assert is_piece_moving((0, 0), pending_moves) is True


def test_is_piece_moving_returns_false_when_piece_is_not_in_pending_moves():
    pending_moves = [make_move("wK", (0, 0), (0, 1))]
    assert is_piece_moving((1, 1), pending_moves) is False


def test_is_piece_moving_returns_false_when_pending_moves_is_empty():
    assert is_piece_moving((0, 0), []) is False


def test_can_start_move_returns_true_when_pending_moves_is_empty():
    assert can_start_move("wR", (0, 0), (0, 3), []) is True


def test_can_start_move_allows_same_color_move_on_same_route():
    pending_moves = [make_move("wN", (1, 0), (1, 3))]
    assert can_start_move("wR", (0, 0), (0, 3), pending_moves) is True


def test_can_start_move_allows_enemy_move_on_different_route():
    pending_moves = [make_move("bR", (0, 0), (3, 0))]
    assert can_start_move("wR", (0, 0), (0, 3), pending_moves) is True


@pytest.mark.parametrize(
    "piece, start, end, pending_move",
    [
        ("wR", (0, 0), (0, 3), make_move("bR", (2, 0), (2, 3))),
        ("wR", (0, 0), (3, 0), make_move("bR", (0, 2), (3, 2))),
        ("wB", (0, 0), (3, 3), make_move("bB", (1, 1), (4, 4))),
    ],
)
def test_can_start_move_blocks_enemy_move_on_same_route(
    piece, start, end, pending_move
):
    assert can_start_move(piece, start, end, [pending_move]) is False


def test_handle_click_does_nothing_when_game_is_over():
    board = make_board(4, 4)
    board[0][0] = "wK"
    session = make_session(board, game_over=True)

    handle_click(session, 0, 0)

    assert session.selected is None
    assert session.pending_moves == []


def test_handle_click_selects_piece_when_nothing_is_selected():
    board = make_board(4, 4)
    board[0][0] = "wK"
    session = make_session(board)

    handle_click(session, 0, 0)

    assert session.selected == (0, 0)
    assert session.pending_moves == []


def test_handle_click_empty_square_without_selection_does_nothing():
    board = make_board(4, 4)
    session = make_session(board)

    handle_click(session, 0, 0)

    assert session.selected is None
    assert session.pending_moves == []


def test_handle_click_does_not_select_piece_that_is_already_moving():
    board = make_board(4, 4)
    board[0][0] = "wK"
    pending_moves = [make_move("wK", (0, 0), (0, 1))]
    session = make_session(board, pending_moves=pending_moves)

    handle_click(session, 0, 0)

    assert session.selected is None
    assert len(session.pending_moves) == 1


def test_handle_click_reselects_piece_of_same_color():
    board = make_board(4, 4)
    board[0][0] = "wK"
    board[0][2] = "wQ"
    session = make_session(board, selected=(0, 0))

    handle_click(session, 0, 2)

    assert session.selected == (0, 2)
    assert session.pending_moves == []


def test_handle_click_valid_move_to_empty_adds_pending_move():
    board = make_board(4, 4)
    board[0][0] = "wK"
    session = make_session(board, selected=(0, 0))

    handle_click(session, 0, 1)

    assert session.selected is None
    assert len(session.pending_moves) == 1
    assert session.pending_moves[0]["piece"] == "wK"
    assert session.pending_moves[0]["start"] == (0, 0)
    assert session.pending_moves[0]["end"] == (0, 1)
    assert session.pending_moves[0]["arrival"] == 1000


def test_handle_click_valid_capture_adds_pending_move():
    board = make_board(4, 4)
    board[0][0] = "wK"
    board[0][1] = "bK"
    session = make_session(board, game_time=500, selected=(0, 0))

    handle_click(session, 0, 1)

    assert session.selected is None
    assert len(session.pending_moves) == 1
    assert session.pending_moves[0]["piece"] == "wK"
    assert session.pending_moves[0]["start"] == (0, 0)
    assert session.pending_moves[0]["end"] == (0, 1)
    assert session.pending_moves[0]["arrival"] == 1500


def test_handle_click_invalid_move_keeps_selection_and_pending_moves():
    board = make_board(4, 4)
    board[0][0] = "wK"
    session = make_session(board, selected=(0, 0))

    handle_click(session, 0, 2)

    assert session.selected == (0, 0)
    assert session.pending_moves == []


def test_handle_click_does_not_add_move_when_route_is_blocked():
    board = make_board(4, 4)
    board[0][0] = "wR"
    pending_moves = [make_move("bR", (2, 0), (2, 3))]
    session = make_session(board, selected=(0, 0), pending_moves=pending_moves)

    handle_click(session, 0, 3)

    assert session.selected == (0, 0)
    assert len(session.pending_moves) == 1
