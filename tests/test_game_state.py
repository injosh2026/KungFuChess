from game_state import GameState


def test_game_state_initializes_with_game_over_false():
    state = GameState()

    assert state.game_over is False


def test_game_state_instances_are_independent():
    first_state = GameState()
    second_state = GameState()

    first_state.game_over = True

    assert first_state.game_over is True
    assert second_state.game_over is False


def test_game_state_game_over_can_be_updated():
    state = GameState()

    state.game_over = True
    assert state.game_over is True

    state.game_over = False
    assert state.game_over is False
