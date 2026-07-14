from kungfu_chess.model.position import Position


class MovementDurationCalculator:
    """
    Calculates the duration required for a piece movement.

    The calculator converts board distance into elapsed time.
    It does not validate movement legality or control the movement itself.
    """

    MOVE_DURATION_PER_CELL_MS = 1000

    @staticmethod
    def calculate(source: Position, target: Position) -> int:
        """
        Calculates movement duration between two board positions.

        Args:
            source:
                Starting position.

            target:
                Destination position.

        Returns:
            Movement duration in milliseconds.
        """
        steps = max(abs(source.row - target.row), abs(source.col - target.col))

        return steps * MovementDurationCalculator.MOVE_DURATION_PER_CELL_MS
