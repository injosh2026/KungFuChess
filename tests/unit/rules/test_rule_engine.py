import pytest

from kungfu_chess.model.board import Board
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.position import Position
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.rules.move_reason import MoveReason

from kungfu_chess.rules.rule_engine import RuleEngine
from kungfu_chess.rules.rook_rule import RookRule
from kungfu_chess.rules.bishop_rule import BishopRule
from kungfu_chess.rules.knight_rule import KnightRule
from kungfu_chess.rules.queen_rule import QueenRule
from kungfu_chess.rules.king_rule import KingRule
from kungfu_chess.rules.pawn_rule import PawnRule


def create_rule_engine():
    return RuleEngine(
        {
            PieceKind.ROOK: RookRule(),
            PieceKind.BISHOP: BishopRule(),
            PieceKind.KNIGHT: KnightRule(),
            PieceKind.QUEEN: QueenRule(),
            PieceKind.KING: KingRule(),
            PieceKind.PAWN: PawnRule(),
        }
    )


def create_rook(position, color=Color.WHITE):
    return Piece(id=1, color=color, kind=PieceKind.ROOK, cell=position)


def create_pawn(position, color=Color.WHITE):
    return Piece(id=2, color=color, kind=PieceKind.PAWN, cell=position)


def test_valid_move_returns_ok():

    board = Board(8, 8)

    rook = Piece(id=1, color=Color.WHITE, kind=PieceKind.ROOK, cell=Position(0, 0))

    board.add_piece(rook)

    engine = create_rule_engine()

    result = engine.validate_move(board, Position(0, 0), Position(0, 5))

    assert result.is_valid is True
    assert result.reason == MoveReason.OK


def test_empty_source_is_invalid():

    board = Board(8, 8)

    engine = create_rule_engine()

    result = engine.validate_move(board, Position(0, 0), Position(0, 5))

    assert result.is_valid is False
    assert result.reason == MoveReason.EMPTY_SOURCE


def test_move_outside_board_is_invalid():

    board = Board(8, 8)

    engine = create_rule_engine()

    result = engine.validate_move(board, Position(9, 0), Position(0, 0))

    assert result.is_valid is False
    assert result.reason == MoveReason.OUTSIDE_BOARD


def test_cannot_move_to_friendly_piece():

    board = Board(8, 8)

    rook = create_rook(Position(0, 0))
    pawn = create_pawn(Position(0, 5))

    board.add_piece(rook)
    board.add_piece(pawn)

    engine = create_rule_engine()

    result = engine.validate_move(board, Position(0, 0), Position(0, 5))

    assert result.is_valid is False
    assert result.reason == MoveReason.FRIENDLY_DESTINATION


def test_illegal_piece_move():

    board = Board(8, 8)

    rook = create_rook(Position(0, 0))

    board.add_piece(rook)

    engine = create_rule_engine()

    result = engine.validate_move(board, Position(0, 0), Position(3, 3))

    assert result.is_valid is False
    assert result.reason == MoveReason.ILLEGAL_PIECE_MOVE


def test_rule_engine_does_not_move_piece():

    board = Board(8, 8)

    rook = create_rook(Position(0, 0))

    board.add_piece(rook)

    engine = create_rule_engine()

    engine.validate_move(board, Position(0, 0), Position(0, 5))

    assert rook.cell == Position(0, 0)
    assert board.get_piece_by_position(Position(0, 5)) is None


def test_can_move_to_enemy_piece():

    board = Board(8, 8)

    rook = create_rook(Position(0, 0))

    enemy = create_pawn(Position(0, 5), Color.BLACK)

    board.add_piece(rook)
    board.add_piece(enemy)

    engine = create_rule_engine()

    result = engine.validate_move(board, Position(0, 0), Position(0, 5))

    assert result.is_valid is True
    assert result.reason == MoveReason.OK
