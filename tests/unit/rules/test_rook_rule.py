import pytest

from kungfu_chess.model.board import Board
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.rules.rook_rule import RookRule


def create_rook(position, color=Color.WHITE):
    return Piece(
        id=1,
        color=color,
        kind=PieceKind.ROOK,
        cell=position
    )


def create_piece(position, color):
    return Piece(
        id=2,
        color=color,
        kind=PieceKind.PAWN,
        cell=position
    )


def test_rook_moves_horizontally_on_empty_row():
    board = Board(8, 8)

    rook = create_rook(Position(3, 3))
    board.add_piece(rook)

    rule = RookRule()

    destinations = rule.legal_destinations(board, rook)

    assert destinations == {
        Position(3, 0),
        Position(3, 1),
        Position(3, 2),
        Position(3, 4),
        Position(3, 5),
        Position(3, 6),
        Position(3, 7),
        Position(0, 3),
        Position(1, 3),
        Position(2, 3),
        Position(4, 3),
        Position(5, 3),
        Position(6, 3),
        Position(7, 3),
    }


def test_rook_stops_before_friendly_piece():
    board = Board(8, 8)

    rook = create_rook(Position(3, 3))
    friendly_piece = create_piece(
        Position(3, 5),
        Color.WHITE
    )

    board.add_piece(rook)
    board.add_piece(friendly_piece)

    rule = RookRule()

    destinations = rule.legal_destinations(board, rook)

    assert Position(3, 4) in destinations
    assert Position(3, 5) not in destinations
    assert Position(3, 6) not in destinations


def test_rook_can_capture_enemy_piece_but_not_pass_through():
    board = Board(8, 8)

    rook = create_rook(Position(3, 3))
    enemy_piece = create_piece(
        Position(3, 5),
        Color.BLACK
    )

    board.add_piece(rook)
    board.add_piece(enemy_piece)

    rule = RookRule()

    destinations = rule.legal_destinations(board, rook)

    assert Position(3, 4) in destinations
    assert Position(3, 5) in destinations
    assert Position(3, 6) not in destinations


def test_rook_does_not_move_outside_board():
    board = Board(8, 8)

    rook = create_rook(Position(0, 0))
    board.add_piece(rook)

    rule = RookRule()

    destinations = rule.legal_destinations(board, rook)

    assert Position(-1, 0) not in destinations
    assert Position(0, -1) not in destinations

    assert Position(0, 1) in destinations
    assert Position(1, 0) in destinations