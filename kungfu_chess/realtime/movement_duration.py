from kungfu_chess.model.position import Position


class MovementDurationCalculator:

    MOVE_DURATION_PER_CELL_MS = 1000

    @staticmethod
    def calculate(source: Position, target: Position) -> int:

        steps = max(abs(source.row - target.row), abs(source.col - target.col))

        return steps * MovementDurationCalculator.MOVE_DURATION_PER_CELL_MS
