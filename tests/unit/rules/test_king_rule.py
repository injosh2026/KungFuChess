from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.rules.king_rule import KingRule


def create_king(position, color=Color.WHITE):
    return Piece(
        id=1,
        color=color,
        kind=PieceKind.KING,
        cell=position
    )


def create_piece(position, color):
    return Piece(
        id=2,
        color=color,
        kind=PieceKind.PAWN,
        cell=position
    )


def test_king_moves_one_square_in_all_directions():
    board = Board(8, 8)

    king = create_king(Position(3, 3))
    board.add_piece(king)

    rule = KingRule()

    destinations = rule.legal_destinations(board, king)

    assert Position(2, 2) in destinations
    assert Position(2, 3) in destinations
    assert Position(2, 4) in destinations
    assert Position(3, 2) in destinations
    assert Position(3, 4) in destinations
    assert Position(4, 2) in destinations
    assert Position(4, 3) in destinations
    assert Position(4, 4) in destinations


def test_king_cannot_move_two_squares():
    board = Board(8, 8)

    king = create_king(Position(3, 3))
    board.add_piece(king)

    rule = KingRule()

    destinations = rule.legal_destinations(board, king)

    assert Position(1, 3) not in destinations
    assert Position(3, 5) not in destinations


def test_king_cannot_capture_friendly_piece():
    board = Board(8, 8)

    king = create_king(Position(3, 3))

    friendly = create_piece(
        Position(2, 2),
        Color.WHITE
    )

    board.add_piece(king)
    board.add_piece(friendly)

    rule = KingRule()

    destinations = rule.legal_destinations(board, king)

    assert Position(2, 2) not in destinations


def test_king_can_capture_enemy_piece():
    board = Board(8, 8)

    king = create_king(Position(3, 3))

    enemy = create_piece(
        Position(2, 2),
        Color.BLACK
    )

    board.add_piece(king)
    board.add_piece(enemy)

    rule = KingRule()

    destinations = rule.legal_destinations(board, king)

    assert Position(2, 2) in destinations


def test_king_does_not_move_outside_board():
    board = Board(8, 8)

    king = create_king(Position(0, 0))
    board.add_piece(king)

    rule = KingRule()

    destinations = rule.legal_destinations(board, king)

    assert Position(-1, -1) not in destinations
    assert Position(-1, 0) not in destinations
    assert Position(0, -1) not in destinations