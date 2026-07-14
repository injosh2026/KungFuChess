from dataclasses import dataclass

from kungfu_chess.model.position import Position


@dataclass(slots=True)
class Motion:
    """
    Represents an active movement of a piece.

    Motion stores the information required to track a piece
    while it is moving between two positions.

    It does not apply movement rules, modify the board,
    or resolve collisions.
    """

    piece_id: int
    start: Position
    target: Position
    duration_ms: int
    elapsed_ms: int = 0

    def advance_time(self, milliseconds: int) -> None:
        """
        Advances the movement clock.

        Args:
            milliseconds:
                Amount of elapsed game time to add.
        """
        self.elapsed_ms += milliseconds

    @property
    def is_completed(self) -> bool:
        """
        Returns whether the movement reached its target time.

        Returns:
            True if elapsed time is greater than or equal
            to the movement duration.
        """
        return self.elapsed_ms >= self.duration_ms
