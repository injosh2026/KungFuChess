from kungfu_chess.model.position import Position
from kungfu_chess.realtime.movement_duration import MovementDurationCalculator

CELL_MS = MovementDurationCalculator.MOVE_DURATION_PER_CELL_MS


def build_path(start: Position, target: Position) -> tuple[Position, ...]:
    """
    Returns every cell along a straight board path.

    Supported paths are horizontal, vertical, and diagonal moves using
    Chebyshev steps. Knight jumps and other non-straight paths are not
    supported here.

    Raises:
        ValueError: If start and target are not on the same row, column,
            or diagonal.
    """
    delta_row = target.row - start.row
    delta_col = target.col - start.col
    steps = max(abs(delta_row), abs(delta_col))

    if steps == 0:
        return (start,)

    same_row = delta_row == 0
    same_col = delta_col == 0
    diagonal = abs(delta_row) == abs(delta_col)

    if not (same_row or same_col or diagonal):
        raise ValueError("Path must be horizontal, vertical, or diagonal")

    row_step = delta_row // steps
    col_step = delta_col // steps

    path = []
    for step in range(steps + 1):
        path.append(
            Position(
                start.row + step * row_step,
                start.col + step * col_step,
            )
        )

    return tuple(path)


def entry_time_ms(path_index: int) -> int:
    """
    Returns the kinematic entry time for a path index.

    Entry time is measured from the start of the motion in milliseconds.
    """
    return path_index * CELL_MS


def mid_path_indices(path: tuple[Position, ...]) -> range:
    """
    Returns indices of cells strictly between start and target.

    Start index 0 and the final target index are excluded.
    """
    if len(path) < 3:
        return range(0)

    return range(1, len(path) - 1)
