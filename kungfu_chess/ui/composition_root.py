"""
Builds all UI dependencies and starts GameApp.

This module is the composition root:
it connects existing components but contains no game logic.
"""

from collections.abc import Callable

from kungfu_chess.config.demo_config import (
    ASSETS_ROOT,
    BOARD_FILENAME,
    PIECE_SET,
    STARTING_BOARD,
)
from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.input.click_router import ClickRouter
from kungfu_chess.input.mouse_input import MouseInput
from kungfu_chess.io.board_parser import BoardParser
from kungfu_chess.model.position import Position
from kungfu_chess.ui.animation_clock import AnimationClock
from kungfu_chess.ui.animation_provider import AnimationProvider
from kungfu_chess.ui.board_coordinates_renderer import BoardCoordinatesRenderer
from kungfu_chess.ui.game_app import GameApp
from kungfu_chess.ui.board_click_mapper import window_coords_to_model_coords
from kungfu_chess.ui.game_ui_layout import layout_for_canvas_size_provider
from kungfu_chess.ui.graphical_renderer import GraphicalRenderer
from kungfu_chess.ui.move_history_panel import MoveHistoryPanel
from kungfu_chess.ui.player_panel import PlayerPanel
from kungfu_chess.ui.player_panel_data import PlayerPanelConfig
from kungfu_chess.ui.promotion_picker_overlay import PromotionPickerOverlay
from kungfu_chess.ui.sprite_library import SpriteLibrary
from kungfu_chess.ui.state_progress_overlay import StateProgressOverlay
from kungfu_chess.view.snapshot_builder import SnapshotBuilder
from kungfu_chess.view.visual_position import VisualPositionCalculator

MODEL_CELL_SIZE = GameFactory.CELL_SIZE
SPRITE_LIBRARY_BOOTSTRAP_CELL_SIZE = 1


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


def to_model_coords(
    x: int,
    y: int,
    canvas_size_provider: Callable[[], tuple[int, int]],
) -> tuple[int, int]:
    """
    Translates a window pixel into the model's pixel space so the unchanged
    board mapper resolves the same cell the user clicked on screen.
    """
    layout = layout_for_canvas_size_provider(canvas_size_provider)
    return window_coords_to_model_coords(
        x,
        y,
        layout,
        MODEL_CELL_SIZE,
    )


def build_app(image) -> GameApp:
    board = BoardParser().parse(STARTING_BOARD)
    controller, game_engine, move_history_observer, score_observer = GameFactory.create(board)

    canvas_size = image.canvas_size

    library = SpriteLibrary(
        ASSETS_ROOT / PIECE_SET,
        ASSETS_ROOT / BOARD_FILENAME,
        SPRITE_LIBRARY_BOOTSTRAP_CELL_SIZE,
    )
    clock = AnimationClock()
    provider = AnimationProvider(library, clock)
    promotion_picker = PromotionPickerOverlay()
    white_history_panel = MoveHistoryPanel("White")
    black_history_panel = MoveHistoryPanel("Black")
    board_coordinates_renderer = BoardCoordinatesRenderer()
    player_panel = PlayerPanel()
    renderer = GraphicalRenderer(
        library,
        canvas_size,
        provider.frame_for,
        StateProgressOverlay(),
        promotion_picker,
        white_history_panel,
        black_history_panel,
        board_coordinates_renderer,
        player_panel,
        PlayerPanelConfig("White", "W"),
        PlayerPanelConfig("Black", "B"),
    )
    visual_position_calculator = CanvasSizedVisualPositionCalculator(canvas_size)

    snapshot_builder = SnapshotBuilder(
        visual_position_calculator,
        get_runtime_progress=game_engine.runtime_progress,
        get_move_history=move_history_observer.entries,
        get_player_scores=score_observer.scores,
    )

    click_router = ClickRouter(
        controller,
        promotion_picker,
        lambda: game_engine.game_state.pending_pawn_promotion,
        lambda x, y: controller.handle_click(
            *to_model_coords(x, y, canvas_size),
        ),
        canvas_size,
    )

    mouse_input = MouseInput(click_router)

    return GameApp(
        game_engine,
        controller,
        snapshot_builder,
        renderer,
        image,
        clock,
        mouse_input,
    )
