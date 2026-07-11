from dataclasses import dataclass

from kungfu_chess.model.position import Position


@dataclass
class Motion:
    piece_id: int
    start: Position
    target: Position
    duration_ms: int
    elapsed_ms: int = 0

    def advance_time(self, milliseconds: int) -> None:
        self.elapsed_ms += milliseconds

    @property
    def is_completed(self) -> bool:
        return self.elapsed_ms >= self.duration_ms
