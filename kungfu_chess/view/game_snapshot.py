from dataclasses import dataclass

from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position


@dataclass(frozen=True)
class PieceSnapshot:
    piece_id: int
    kind: PieceKind
    color: Color
    pixel_position: tuple[int, int]
    state: PieceState


@dataclass(frozen=True)
class GameSnapshot:
    board_width: int
    board_height: int
    pieces: list[PieceSnapshot]
    selected_cell: Position | None
    game_over: bool