from dataclasses import dataclass, field

from kungfu_chess.model.board import Board
from kungfu_chess.model.piece_color import Color
from kungfu_chess.rules.pawn_end_outcome import PendingPawnPromotion


@dataclass(slots=True)
class GameState:
    """
    Stores the mutable state of an active game.

    GameState contains the logical board and global game information
    such as game completion, winner, and scores.

    It does not contain movement rules, input handling,
    rendering logic, or time management.
    """
    board: Board
    game_over: bool = False
    winner: Color | None = None
    pending_pawn_promotion: PendingPawnPromotion | None = None
    scores: dict = field(
        default_factory=lambda: {
            Color.WHITE: 0,
            Color.BLACK: 0,
        }
    )
