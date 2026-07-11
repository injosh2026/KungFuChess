from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.rules.queen_rule import QueenRule


def create_queen(position, color=Color.WHITE):
    return Piece(id=1, color=color, kind=PieceKind.QUEEN, cell=position)


def create_piece(position, color):
    return Piece(id=2, color=color, kind=PieceKind.PAWN, cell=position)


def test_queen_moves_like_rook_and_bishop():
    board = Board(8, 8)

    queen = create_queen(Position(3, 3))
    board.add_piece(queen)

    rule = QueenRule()

    destinations = rule.legal_destinations(board, queen)

    # straight
    assert Position(3, 4) in destinations
    assert Position(4, 3) in destinations

    # diagonal
    assert Position(2, 2) in destinations
    assert Position(4, 4) in destinations


def test_queen_stops_before_friendly_piece():
    board = Board(8, 8)

    queen = create_queen(Position(3, 3))

    friendly = create_piece(Position(3, 5), Color.WHITE)

    board.add_piece(queen)
    board.add_piece(friendly)

    rule = QueenRule()

    destinations = rule.legal_destinations(board, queen)

    assert Position(3, 4) in destinations
    assert Position(3, 5) not in destinations
    assert Position(3, 6) not in destinations


def test_queen_can_capture_enemy_piece():
    board = Board(8, 8)

    queen = create_queen(Position(3, 3))

    enemy = create_piece(Position(3, 5), Color.BLACK)

    board.add_piece(queen)
    board.add_piece(enemy)

    rule = QueenRule()

    destinations = rule.legal_destinations(board, queen)

    assert Position(3, 5) in destinations
    assert Position(3, 6) not in destinations
