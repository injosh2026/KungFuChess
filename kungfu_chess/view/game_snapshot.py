from dataclasses import dataclass

from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
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
    state: str
    visual_position: tuple[float, float] | None = None
    state_progress: float | None = None


@dataclass(frozen=True, slots=True)
class PromotionSnapshot:
    """
    Immutable promotion choice data for rendering and input routing.

    Built from pending pawn promotion state without exposing GameState.
    """

    piece_id: int
    position: Position
    color: Color
    allowed_kinds: frozenset[PieceKind]


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
    legal_moves: set[Position]
    game_over: bool
    winner: Color | None = None
    pending_promotion: PromotionSnapshot | None = None