from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Rect:
    """Axis-aligned rectangle in window pixel coordinates."""

    x: int
    y: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height
