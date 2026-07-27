from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.view.move_history_entry import MoveHistoryEntry
from kungfu_chess.view.runtime_role import RuntimeRole

EMPTY_RUNTIME_PROGRESS: Mapping[RuntimeRole, float] = MappingProxyType({})
EMPTY_PLAYER_SCORES: Mapping[str, int] = MappingProxyType({})


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
    runtime_progress: Mapping[RuntimeRole, float] = field(
        default=EMPTY_RUNTIME_PROGRESS,
    )


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
    move_history: tuple[MoveHistoryEntry, ...] = ()
    player_scores: Mapping[str, int] = EMPTY_PLAYER_SCORES
