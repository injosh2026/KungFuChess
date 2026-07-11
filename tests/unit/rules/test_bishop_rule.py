from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.rules.bishop_rule import BishopRule


def create_bishop(position, color=Color.WHITE):
    return Piece(id=1, color=color, kind=PieceKind.BISHOP, cell=position)


def create_piece(position, color):
    return Piece(id=2, color=color, kind=PieceKind.PAWN, cell=position)


def test_bishop_moves_diagonally_on_empty_board():
    board = Board(8, 8)

    bishop = create_bishop(Position(3, 3))
    board.add_piece(bishop)

    rule = BishopRule()

    destinations = rule.legal_destinations(board, bishop)

    assert Position(2, 2) in destinations
    assert Position(1, 1) in destinations
    assert Position(0, 0) in destinations

    assert Position(2, 4) in destinations
    assert Position(1, 5) in destinations

    assert Position(4, 4) in destinations
    assert Position(5, 5) in destinations


def test_bishop_does_not_move_straight():
    board = Board(8, 8)

    bishop = create_bishop(Position(3, 3))
    board.add_piece(bishop)

    rule = BishopRule()

    destinations = rule.legal_destinations(board, bishop)

    assert Position(3, 4) not in destinations
    assert Position(4, 3) not in destinations


def test_bishop_stops_before_friendly_piece():
    board = Board(8, 8)

    bishop = create_bishop(Position(3, 3))

    friendly = create_piece(Position(1, 1), Color.WHITE)

    board.add_piece(bishop)
    board.add_piece(friendly)

    rule = BishopRule()

    destinations = rule.legal_destinations(board, bishop)

    assert Position(2, 2) in destinations
    assert Position(1, 1) not in destinations
    assert Position(0, 0) not in destinations


def test_bishop_can_capture_enemy_but_not_pass_through():
    board = Board(8, 8)

    bishop = create_bishop(Position(3, 3))

    enemy = create_piece(Position(1, 1), Color.BLACK)

    board.add_piece(bishop)
    board.add_piece(enemy)

    rule = BishopRule()

    destinations = rule.legal_destinations(board, bishop)

    assert Position(2, 2) in destinations
    assert Position(1, 1) in destinations
    assert Position(0, 0) not in destinations
