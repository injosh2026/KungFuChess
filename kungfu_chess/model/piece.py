from dataclasses import dataclass

from .piece_color import Color
from .piece_kind import PieceKind
from .piece_state import PieceState
from .position import Position


@dataclass(slots=True)
class Piece:
    """
    Represents a game piece.

    A Piece stores only its identity and current state.
    Movement rules, timing, rendering, and game logic are
    handled by other components.
    """

    id: int
    color: Color
    kind: PieceKind
    cell: Position
    state: PieceState = PieceState.IDLE
