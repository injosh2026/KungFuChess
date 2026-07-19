from dataclasses import dataclass

from kungfu_chess.events.game_event import GameEvent
from kungfu_chess.model.position import Position


@dataclass(frozen=True, slots=True)
class MovePerformedEvent(GameEvent):
    """
    Published when a piece completes a board move.

    Contains domain facts only. Presentation formatting belongs in
    history entries and UI panels.
    """

    piece_id: int
    piece_code: str
    piece_name: str
    from_position: Position
    to_position: Position
    capture: str | None = None
    promotion: str | None = None
    jump_used: bool = False
