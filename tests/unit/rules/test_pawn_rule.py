from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.rules.pawn_rule import PawnRule


def create_pawn(position, color=Color.WHITE):
    return Piece(id=1, color=color, kind=PieceKind.PAWN, cell=position)


def create_piece(position, color):
    return Piece(id=2, color=color, kind=PieceKind.ROOK, cell=position)


def test_white_pawn_moves_forward():
    board = Board(8, 8)

    pawn = create_pawn(Position(4, 3), Color.WHITE)
    board.add_piece(pawn)

    rule = PawnRule()

    destinations = rule.legal_destinations(board, pawn)

    assert Position(3, 3) in destinations


def test_black_pawn_moves_forward():
    board = Board(8, 8)

    pawn = create_pawn(Position(3, 3), Color.BLACK)
    board.add_piece(pawn)

    rule = PawnRule()

    destinations = rule.legal_destinations(board, pawn)

    assert Position(4, 3) in destinations


def test_pawn_cannot_move_forward_into_piece():
    board = Board(8, 8)

    pawn = create_pawn(Position(4, 3), Color.WHITE)

    blocker = create_piece(Position(3, 3), Color.BLACK)

    board.add_piece(pawn)
    board.add_piece(blocker)

    rule = PawnRule()

    destinations = rule.legal_destinations(board, pawn)

    assert Position(3, 3) not in destinations


def test_white_pawn_can_capture_diagonally():
    board = Board(8, 8)

    pawn = create_pawn(Position(4, 3), Color.WHITE)

    enemy = create_piece(Position(3, 2), Color.BLACK)

    board.add_piece(pawn)
    board.add_piece(enemy)

    rule = PawnRule()

    destinations = rule.legal_destinations(board, pawn)

    assert Position(3, 2) in destinations


def test_pawn_cannot_capture_friendly_piece():
    board = Board(8, 8)

    pawn = create_pawn(Position(4, 3), Color.WHITE)

    friendly = create_piece(Position(3, 2), Color.WHITE)

    board.add_piece(pawn)
    board.add_piece(friendly)

    rule = PawnRule()

    destinations = rule.legal_destinations(board, pawn)

    assert Position(3, 2) not in destinations


def test_pawn_has_no_two_square_move_off_starting_rank():
    board = Board(8, 8)

    pawn = create_pawn(Position(4, 3), Color.WHITE)
    board.add_piece(pawn)

    rule = PawnRule()

    destinations = rule.legal_destinations(board, pawn)

    assert Position(2, 3) not in destinations


def test_white_pawn_can_move_two_squares_from_starting_rank_on_first_move():
    board = Board(8, 8)

    pawn = create_pawn(Position(6, 3), Color.WHITE)
    board.add_piece(pawn)

    rule = PawnRule()

    destinations = rule.legal_destinations(board, pawn)

    assert Position(5, 3) in destinations
    assert Position(4, 3) in destinations


def test_pawn_cannot_move_two_squares_after_has_moved():
    board = Board(8, 8)

    pawn = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.PAWN,
        cell=Position(6, 3),
        has_moved=True,
    )
    board.add_piece(pawn)

    rule = PawnRule()

    destinations = rule.legal_destinations(board, pawn)

    assert Position(5, 3) in destinations
    assert Position(4, 3) not in destinations


def test_pawn_cannot_double_step_with_blocked_intermediate_cell():
    board = Board(8, 8)

    pawn = create_pawn(Position(6, 3), Color.WHITE)
    blocker = create_piece(Position(5, 3), Color.BLACK)

    board.add_piece(pawn)
    board.add_piece(blocker)

    rule = PawnRule()

    destinations = rule.legal_destinations(board, pawn)

    assert Position(5, 3) not in destinations
    assert Position(4, 3) not in destinations


def test_pawn_cannot_double_step_with_blocked_destination_cell():
    board = Board(8, 8)

    pawn = create_pawn(Position(6, 3), Color.WHITE)
    blocker = create_piece(Position(4, 3), Color.BLACK)

    board.add_piece(pawn)
    board.add_piece(blocker)

    rule = PawnRule()

    destinations = rule.legal_destinations(board, pawn)

    assert Position(5, 3) in destinations
    assert Position(4, 3) not in destinations
