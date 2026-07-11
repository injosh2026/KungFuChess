from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece_color import Color


def test_game_state_creation():

    board = Board(8, 8)

    state = GameState(board)

    assert state.board is board
    assert state.game_over is False
    assert state.winner is None


def test_game_state_has_initial_scores():

    board = Board(8, 8)

    state = GameState(board)

    assert state.scores[Color.WHITE] == 0
    assert state.scores[Color.BLACK] == 0


def test_game_state_scores_are_independent():

    first_board = Board(8, 8)
    second_board = Board(8, 8)

    first_state = GameState(first_board)
    second_state = GameState(second_board)

    first_state.scores[Color.WHITE] = 10

    assert second_state.scores[Color.WHITE] == 0


def test_game_state_can_store_winner():

    board = Board(8, 8)

    state = GameState(board)

    state.game_over = True
    state.winner = Color.WHITE

    assert state.game_over is True
    assert state.winner == Color.WHITE