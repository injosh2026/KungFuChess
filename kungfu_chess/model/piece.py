from dataclasses import dataclass

from .piece_color import Color
from .piece_kind import PieceKind
from .piece_state import PieceState
from .position import Position

@dataclass
class Piece:
    id: int
    color: Color
    kind: PieceKind
    cell: Position
    state: PieceState = PieceState.IDLE