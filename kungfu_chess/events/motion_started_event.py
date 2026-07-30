from dataclasses import dataclass

from kungfu_chess.events.game_event import GameEvent
from kungfu_chess.model.position import Position


@dataclass(frozen=True, slots=True)
class MotionStartedEvent(GameEvent):
    """
    Published when a piece begins a board move.

    Contains domain facts only. Client-side interpolation uses this
    as a presentation hint; the board remains authoritative via snapshots.
    """

    piece_id: int
    start: Position
    target: Position
    duration_ms: int
    state: str
