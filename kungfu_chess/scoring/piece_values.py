from kungfu_chess.model.piece_kind import PieceKind

PIECE_VALUES = {
    PieceKind.PAWN: 1,
    PieceKind.KNIGHT: 3,
    PieceKind.BISHOP: 3,
    PieceKind.ROOK: 5,
    PieceKind.QUEEN: 9,
    PieceKind.KING: 0,
}


def piece_value(kind: PieceKind) -> int:
    return PIECE_VALUES[kind]
