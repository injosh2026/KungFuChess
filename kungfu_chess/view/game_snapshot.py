from dataclasses import dataclass

from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position


@dataclass(frozen=True, slots=True)
class PieceSnapshot:
    """
    Immutable representation of a piece state for rendering.

    A snapshot contains only presentation data and does not
    affect the actual game state.
    """
    piece_id: int
    kind: PieceKind
    color: Color
    position: Position
    state: PieceState


@dataclass(frozen=True, slots=True)
class GameSnapshot:
    """
    Immutable representation of the complete game state
    at a specific moment.

    Used by rendering layers and external consumers without
    exposing mutable game objects.
    """
    board_width: int
    board_height: int
    pieces: list[PieceSnapshot]
    selected_cell: Position | None
    game_over: bool
    winner: Color | None = None