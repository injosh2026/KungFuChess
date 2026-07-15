from kungfu_chess.model.piece import Piece
from kungfu_chess.model.position import Position
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_state import PieceState


def test_piece_creation():
    piece = Piece(id=1, color=Color.WHITE, kind=PieceKind.KING, cell=Position(0, 4))

    assert piece.id == 1
    assert piece.color == Color.WHITE
    assert piece.kind == PieceKind.KING
    assert piece.cell == Position(0, 4)
    assert piece.state == PieceState.IDLE


def test_piece_state_can_change():
    piece = Piece(id=1, color=Color.BLACK, kind=PieceKind.PAWN, cell=Position(1, 0))

    piece.state = PieceState.MOVING

    assert piece.state == PieceState.MOVING


def test_piece_accepts_any_state_string():
    piece = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0),
        state="jump",
    )

    assert piece.state == "jump"
