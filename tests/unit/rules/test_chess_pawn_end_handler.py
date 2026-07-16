from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.rules.chess_pawn_end_handler import ChessPawnEndHandler


def create_pawn(color, row, col=3):
    return Piece(
        id=1,
        color=color,
        kind=PieceKind.PAWN,
        cell=Position(row, col),
    )


def test_white_pawn_on_promotion_rank_returns_pending_choice():
    board = Board(8, 8)
    pawn = create_pawn(Color.WHITE, 0)
    board.add_piece(pawn)
    handler = ChessPawnEndHandler()

    outcome = handler.resolve(pawn, Position(0, 3), board)

    assert outcome.new_kind is None
    assert outcome.pending_choice_kinds == ChessPawnEndHandler.PROMOTION_KINDS
    assert outcome.blocks_state_transition is True


def test_black_pawn_on_promotion_rank_returns_pending_choice():
    board = Board(8, 8)
    pawn = create_pawn(Color.BLACK, 7)
    board.add_piece(pawn)
    handler = ChessPawnEndHandler()

    outcome = handler.resolve(pawn, Position(7, 3), board)

    assert outcome.pending_choice_kinds == ChessPawnEndHandler.PROMOTION_KINDS


def test_pending_choice_includes_queen_rook_bishop_knight():
    board = Board(8, 8)
    pawn = create_pawn(Color.WHITE, 0)
    board.add_piece(pawn)
    handler = ChessPawnEndHandler()

    outcome = handler.resolve(pawn, Position(0, 3), board)

    assert outcome.pending_choice_kinds == frozenset(
        {
            PieceKind.QUEEN,
            PieceKind.ROOK,
            PieceKind.BISHOP,
            PieceKind.KNIGHT,
        }
    )


def test_pawn_not_on_promotion_rank_returns_no_action():
    board = Board(8, 8)
    pawn = create_pawn(Color.WHITE, 4)
    board.add_piece(pawn)
    handler = ChessPawnEndHandler()

    outcome = handler.resolve(pawn, Position(4, 3), board)

    assert outcome.pending_choice_kinds is None
    assert outcome.new_kind is None
    assert outcome.blocks_state_transition is False


def test_non_pawn_on_promotion_rank_returns_no_action():
    board = Board(8, 8)
    queen = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.QUEEN,
        cell=Position(0, 3),
    )
    board.add_piece(queen)
    handler = ChessPawnEndHandler()

    outcome = handler.resolve(queen, Position(0, 3), board)

    assert outcome.pending_choice_kinds is None
