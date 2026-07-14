import pytest

from kungfu_chess.model.board import Board
from kungfu_chess.model.position import Position
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind


def create_piece(position, piece_id=1):
    return Piece(id=piece_id, color=Color.WHITE, kind=PieceKind.KING, cell=position)


def test_empty_cell_returns_none():
    board = Board(8, 8)

    assert board.get_piece_by_position(Position(0, 0)) is None


def test_add_and_get_piece():
    board = Board(8, 8)

    piece = create_piece(Position(0, 0))

    board.add_piece(piece)

    assert board.get_piece_by_position(Position(0, 0)) == piece


def test_cannot_add_two_pieces_same_cell():
    board = Board(8, 8)

    board.add_piece(create_piece(Position(0, 0), 1))

    another = create_piece(Position(0, 0), 2)

    with pytest.raises(ValueError):
        board.add_piece(another)


def test_cannot_add_two_pieces_same_id():
    board = Board(8, 8)

    first = create_piece(Position(0, 0), 1)
    second = create_piece(Position(0, 1), 1)

    board.add_piece(first)

    with pytest.raises(ValueError):
        board.add_piece(second)


def test_move_piece_updates_position():
    board = Board(8, 8)

    piece = create_piece(Position(0, 0))

    board.add_piece(piece)

    board.move_piece(Position(0, 0), Position(0, 1))

    assert board.get_piece_by_position(Position(0, 0)) is None
    assert board.get_piece_by_position(Position(0, 1)) == piece
    assert piece.cell == Position(0, 1)


def test_move_piece_keeps_id_lookup():
    board = Board(8, 8)

    piece = create_piece(Position(0, 0), 10)

    board.add_piece(piece)

    board.move_piece(Position(0, 0), Position(0, 1))

    assert board.get_piece_by_id(10) == piece


def test_remove_piece():
    board = Board(8, 8)

    piece = create_piece(Position(0, 0))

    board.add_piece(piece)

    removed = board.remove_piece(Position(0, 0))

    assert removed == piece
    assert board.get_piece_by_position(Position(0, 0)) is None


def test_remove_piece_removes_id_reference():
    board = Board(8, 8)

    piece = create_piece(Position(0, 0), 5)

    board.add_piece(piece)

    board.remove_piece(Position(0, 0))

    assert board.get_piece_by_id(5) is None


def test_cannot_add_piece_outside_board():
    board = Board(8, 8)

    piece = create_piece(Position(8, 0))

    with pytest.raises(ValueError):
        board.add_piece(piece)


def test_move_piece_captures_piece_on_target_cell():

    board = Board(8, 8)

    first = create_piece(Position(0, 0), 1)
    second = create_piece(Position(0, 1), 2)

    board.add_piece(first)
    board.add_piece(second)

    captured = board.move_piece(
        Position(0, 0),
        Position(0, 1)
    )

    assert captured is second

    assert board.get_piece_by_position(Position(0, 0)) is None

    assert board.get_piece_by_position(Position(0, 1)) is first

    assert board.get_piece_by_id(1) is first
    assert board.get_piece_by_id(2) is None


def test_get_piece_by_id():
    board = Board(8, 8)

    piece = create_piece(Position(0, 0), 20)

    board.add_piece(piece)

    assert board.get_piece_by_id(20) == piece


def test_move_piece_moves_piece_to_target():

    board = Board(8, 8)

    piece = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0)
    )

    board.add_piece(piece)

    captured = board.move_piece(
        Position(0, 0),
        Position(0, 1)
    )

    assert captured is None

    assert board.get_piece_by_position(Position(0, 0)) is None

    moved_piece = board.get_piece_by_position(Position(0, 1))

    assert moved_piece is piece
    assert moved_piece.cell == Position(0, 1)

    assert board.get_piece_by_id(1) is piece


def test_move_piece_captures_target_piece():

    board = Board(8, 8)

    attacker = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0)
    )

    victim = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.PAWN,
        cell=Position(0, 1)
    )

    board.add_piece(attacker)
    board.add_piece(victim)

    captured = board.move_piece(
        Position(0, 0),
        Position(0, 1)
    )

    assert captured is victim

    assert board.get_piece_by_position(Position(0, 0)) is None

    assert board.get_piece_by_position(Position(0, 1)) is attacker

    assert board.get_piece_by_id(2) is None

    assert board.get_piece_by_id(1) is attacker