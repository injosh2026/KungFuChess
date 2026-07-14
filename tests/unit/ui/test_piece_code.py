from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.ui.piece_code import piece_code


def test_queen_white_maps_to_qw():
    assert piece_code(PieceKind.QUEEN, Color.WHITE) == "QW"


def test_pawn_black_maps_to_pb():
    assert piece_code(PieceKind.PAWN, Color.BLACK) == "PB"


def test_knight_uses_n_letter():
    assert piece_code(PieceKind.KNIGHT, Color.WHITE) == "NW"


def test_all_kinds_and_colors_produce_two_letter_codes():
    codes = {
        piece_code(kind, color)
        for kind in PieceKind
        for color in Color
    }

    assert len(codes) == len(PieceKind) * len(Color)
    assert all(len(code) == 2 for code in codes)
