from kungfu_chess.input.board_mapper import BoardMapper
from kungfu_chess.model.board import Board

CELL_SIZE = 100

def create_mapper():
    return BoardMapper(CELL_SIZE)

def create_board():
    return Board(8, 8)


def test_maps_first_cell():
    mapper = create_mapper()

    position = mapper.pixel_to_position(create_board(), 50, 50)

    assert position.row == 0
    assert position.col == 0


def test_maps_second_column():
    mapper = create_mapper()

    position = mapper.pixel_to_position(create_board(), 150, 50)

    assert position.row == 0
    assert position.col == 1


def test_maps_second_row():
    mapper = create_mapper()

    position = mapper.pixel_to_position(create_board(), 50, 150)

    assert position.row == 1
    assert position.col == 0


def test_returns_none_when_click_outside_board():
    mapper = create_mapper()

    position = mapper.pixel_to_position(create_board(), 850, 50)

    assert position is None


def test_cell_boundary():
    mapper = create_mapper()

    first = mapper.pixel_to_position(create_board(), 99, 99)
    second = mapper.pixel_to_position(create_board(), 100, 100)

    assert first.row == 0
    assert first.col == 0

    assert second.row == 1
    assert second.col == 1