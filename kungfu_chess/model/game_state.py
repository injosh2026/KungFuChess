from dataclasses import dataclass, field

from kungfu_chess.model.board import Board
from kungfu_chess.model.piece_color import Color


@dataclass
class GameState:
    board: Board
    game_over: bool = False
    winner: Color | None = None
    scores: dict[Color, int] = field(
        default_factory=lambda: {
            Color.WHITE: 0,
            Color.BLACK: 0,
        }
    )