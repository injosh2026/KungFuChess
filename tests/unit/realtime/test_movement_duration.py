from kungfu_chess.model.position import Position
from kungfu_chess.realtime.movement_duration import MovementDurationCalculator


def test_one_square_move_takes_one_second():

    duration = MovementDurationCalculator.calculate(Position(0, 0), Position(0, 1))

    assert duration == 1000


def test_five_square_horizontal_move():

    duration = MovementDurationCalculator.calculate(Position(0, 0), Position(0, 5))

    assert duration == 5000


def test_diagonal_move_uses_cell_steps():

    duration = MovementDurationCalculator.calculate(Position(0, 0), Position(3, 3))

    assert duration == 3000


def test_vertical_move():

    duration = MovementDurationCalculator.calculate(Position(2, 4), Position(6, 4))

    assert duration == 4000
