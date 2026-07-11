from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.rules.knight_rule import KnightRule


def create_knight(position, color=Color.WHITE):
    return Piece(
        id=1,
        color=color,
        kind=PieceKind.KNIGHT,
        cell=position
    )


def create_piece(position, color):
    return Piece(
        id=2,
        color=color,
        kind=PieceKind.PAWN,
        cell=position
    )


def test_knight_moves_in_l_shape():
    board = Board(8, 8)

    knight = create_knight(Position(3, 3))
    board.add_piece(knight)

    rule = KnightRule()

    destinations = rule.legal_destinations(board, knight)

    assert Position(1, 2) in destinations
    assert Position(1, 4) in destinations
    assert Position(5, 2) in destinations
    assert Position(5, 4) in destinations


def test_knight_jumps_over_blockers():
    board = Board(8, 8)

    knight = create_knight(Position(3, 3))

    blocker1 = create_piece(
        Position(2, 3),
        Color.WHITE
    )

    blocker2 = create_piece(
        Position(3, 2),
        Color.WHITE
    )

    board.add_piece(knight)
    board.add_piece(blocker1)
    board.add_piece(blocker2)

    rule = KnightRule()

    destinations = rule.legal_destinations(board, knight)

    assert Position(1, 2) in destinations
    assert Position(1, 4) in destinations


def test_knight_cannot_capture_friendly_piece():
    board = Board(8, 8)

    knight = create_knight(Position(3, 3))

    friendly = create_piece(
        Position(1, 2),
        Color.WHITE
    )

    board.add_piece(knight)
    board.add_piece(friendly)

    rule = KnightRule()

    destinations = rule.legal_destinations(board, knight)

    assert Position(1, 2) not in destinations


def test_knight_can_capture_enemy_piece():
    board = Board(8, 8)

    knight = create_knight(Position(3, 3))

    enemy = create_piece(
        Position(1, 2),
        Color.BLACK
    )

    board.add_piece(knight)
    board.add_piece(enemy)

    rule = KnightRule()

    destinations = rule.legal_destinations(board, knight)

    assert Position(1, 2) in destinations


def test_knight_can_move_to_empty_square():
    board = Board(8, 8)

    knight = create_knight(Position(3, 3))
    board.add_piece(knight)

    rule = KnightRule()

    destinations = rule.legal_destinations(board, knight)
    print(destinations)

    assert Position(1, 2) in destinations

def test_knight_can_capture_enemy_piece():
    board = Board(8, 8)

    knight = create_knight(Position(3, 3))

    enemy = create_piece(
        Position(5, 4),
        Color.BLACK
    )

    board.add_piece(knight)
    board.add_piece(enemy)

    rule = KnightRule()

    destinations = rule.legal_destinations(board, knight)

    assert Position(5, 4) in destinations