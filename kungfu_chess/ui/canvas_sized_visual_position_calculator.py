from collections.abc import Callable

from kungfu_chess.model.position import Position
from kungfu_chess.ui.game_ui_layout import layout_for_canvas_size_provider
from kungfu_chess.view.visual_position import VisualPositionCalculator


class CanvasSizedVisualPositionCalculator:
    """Adapts visual interpolation to the current responsive cell size."""

    def __init__(self, canvas_size_provider: Callable[[], tuple[int, int]]):
        self._canvas_size_provider = canvas_size_provider

    def calculate(
        self,
        start: Position,
        target: Position,
        progress: float,
    ) -> tuple[float, float]:
        layout = layout_for_canvas_size_provider(self._canvas_size_provider)
        calculator = VisualPositionCalculator(layout.display_cell_size)
        return calculator.calculate(start, target, progress)
