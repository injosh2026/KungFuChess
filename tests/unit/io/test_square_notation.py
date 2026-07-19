from kungfu_chess.io.square_notation import position_to_square
from kungfu_chess.model.position import Position


def test_position_to_square_maps_top_row_to_rank_eight():
    assert position_to_square(Position(0, 0)) == "a8"


def test_position_to_square_maps_white_pawn_starting_square():
    assert position_to_square(Position(6, 0)) == "a2"


def test_position_to_square_maps_one_step_pawn_advance():
    assert position_to_square(Position(5, 0)) == "a3"


def test_position_to_square_maps_top_right_corner():
    assert position_to_square(Position(1, 7)) == "h7"
