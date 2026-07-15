from dataclasses import dataclass

from kungfu_chess.model.position import Position


@dataclass(frozen=True, slots=True)
class MotionSnapshot:
    piece_id: int
    start: Position
    target: Position
    progress: float