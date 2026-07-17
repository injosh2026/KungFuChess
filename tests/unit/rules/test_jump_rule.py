from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.rules.chess_pawn_end_handler import ChessPawnEndHandler
from kungfu_chess.rules.jump_rule import JumpRule
from kungfu_chess.rules.pawn_end_outcome import PendingPawnPromotion


def create_state():
    board = Board(8, 8)
    piece = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.KNIGHT,
        cell=Position(0, 0),
    )
    board.add_piece(piece)
    return GameState(board), piece


def test_can_jump_when_game_is_active():
    state, piece = create_state()
    rule = JumpRule()

    assert rule.can_jump(state, piece) is True


def test_can_jump_false_when_promotion_pending():
    state, piece = create_state()
    state.pending_pawn_promotion = PendingPawnPromotion(
        piece_id=piece.id,
        allowed_kinds=ChessPawnEndHandler.PROMOTION_KINDS,
    )
    rule = JumpRule()

    assert rule.can_jump(state, piece) is False


def test_can_jump_false_when_game_over():
    state, piece = create_state()
    state.game_over = True
    rule = JumpRule()

    assert rule.can_jump(state, piece) is False
