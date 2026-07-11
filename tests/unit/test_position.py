from kungfu_chess.model.position import Position

def test_positions_with_same_coordinates_are_equal():
    position1 = Position(2, 3)
    position2 = Position(2, 3)

    assert position1 == position2

def test_positions_with_different_coordinates_are_not_equal():
    position1 = Position(2, 3)
    position2 = Position(2, 4)

    assert position1 != position2