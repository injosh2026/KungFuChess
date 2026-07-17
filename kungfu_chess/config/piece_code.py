from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind

KIND_CODES = {
    PieceKind.KING: "K",
    PieceKind.QUEEN: "Q",
    PieceKind.ROOK: "R",
    PieceKind.BISHOP: "B",
    PieceKind.KNIGHT: "N",
    PieceKind.PAWN: "P",
}

COLOR_CODES = {
    Color.WHITE: "W",
    Color.BLACK: "B",
}


def piece_code(kind: PieceKind, color: Color) -> str:
    """
    Maps a piece kind and color to its asset code.

    Example:
        Queen + White -> "QW"
    """
    return f"{KIND_CODES[kind]}{COLOR_CODES[color]}"
