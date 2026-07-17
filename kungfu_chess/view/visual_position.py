from kungfu_chess.model.position import Position


class VisualPositionCalculator:
    """
    Calculates pixel position of a moving piece.

    Converts board movement progress into a visual
    pixel position for rendering.
    """

    def __init__(self, cell_size: int):
        self._cell_size = cell_size

    def calculate(
        self,
        start: Position,
        target: Position,
        progress: float,
    ) -> tuple[float, float]:

        half_cell = self._cell_size / 2

        start_x = start.col * self._cell_size + half_cell
        start_y = start.row * self._cell_size + half_cell

        target_x = target.col * self._cell_size + half_cell
        target_y = target.row * self._cell_size + half_cell

        x = start_x + (target_x - start_x) * progress
        y = start_y + (target_y - start_y) * progress

        return x, y
