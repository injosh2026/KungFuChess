import pytest

from kungfu_chess.model.board import Board
from kungfu_chess.model.position import Position
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind


def create_piece(position):
    return Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.KING,
        cell=position
    )


def test_empty_cell_returns_none():
    board = Board(8, 8)

    assert board.get_piece(Position(0, 0)) is None


def test_add_and_get_piece():
    board = Board(8, 8)
    piece = create_piece(Position(0, 0))

    board.add_piece(piece)

    assert board.get_piece(Position(0, 0)) == piece


def test_cannot_add_two_pieces_same_cell():
    board = Board(8, 8)

    board.add_piece(create_piece(Position(0, 0)))

    another = create_piece(Position(0, 0))

    try:
        board.add_piece(another)
        assert False
    except ValueError:
        assert True


def test_move_piece_updates_position():
    board = Board(8, 8)
    piece = create_piece(Position(0, 0))

    board.add_piece(piece)

    board.move_piece(
        Position(0, 0),
        Position(0, 1)
    )

    assert board.get_piece(Position(0, 0)) is None
    assert board.get_piece(Position(0, 1)) == piece
    assert piece.cell == Position(0, 1)


def test_remove_piece():
    board = Board(8, 8)
    piece = create_piece(Position(0, 0))

    board.add_piece(piece)

    removed = board.remove_piece(Position(0, 0))

    assert removed == piece
    assert board.get_piece(Position(0, 0)) is None


def test_cannot_add_piece_outside_board():
    board = Board(8, 8)

    piece = create_piece(Position(8, 0))

    with pytest.raises(ValueError):
        board.add_piece(piece)


def test_cannot_move_piece_to_occupied_cell():
    board = Board(8, 8)

    first = create_piece(Position(0, 0))
    second = create_piece(Position(0, 1))

    board.add_piece(first)
    board.add_piece(second)

    with pytest.raises(ValueError):
        board.move_piece(
            Position(0, 0),
            Position(0, 1)
        )