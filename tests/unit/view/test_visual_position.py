from kungfu_chess.model.position import Position
from kungfu_chess.view.visual_position import VisualPositionCalculator


def test_calculates_middle_of_motion():

    calculator = VisualPositionCalculator(100)

    result = calculator.calculate(
        Position(0, 0),
        Position(2, 0),
        0.5,
    )

    assert result == (0, 100)