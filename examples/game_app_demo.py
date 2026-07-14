"""
Composition root for the interactive demo.

This is the single entry point that builds every dependency and starts
GameApp.run(). It only wires already-existing components together; it adds
no game logic.

Display geometry (a smaller board with a margin around it) lives entirely
in this display layer: the board is drawn shrunk and offset by a margin,
and mouse coordinates are translated back into the model's pixel space
before reaching the unchanged controller. The backend (engine, controller,
board mapper) is untouched.

Run from the KungFuChess directory:

    python -m examples.game_app_demo
"""

from examples.demo_ui import (
    ASSET_STATE_BY_PIECE_STATE,
    ASSETS_ROOT,
    BOARD_FILENAME,
    PIECE_SET,
    STARTING_BOARD,
)
from img import Img
from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.input.mouse_input import MouseInput
from kungfu_chess.io.board_parser import BoardParser
from kungfu_chess.ui.animation_clock import AnimationClock
from kungfu_chess.ui.animation_provider import AnimationProvider
from kungfu_chess.ui.game_app import GameApp
from kungfu_chess.ui.graphical_renderer import GraphicalRenderer
from kungfu_chess.ui.sprite_library import BOARD_CELLS_PER_SIDE, SpriteLibrary
from kungfu_chess.view.snapshot_builder import SnapshotBuilder

DISPLAY_CELL_SIZE = 90
BOARD_MARGIN = 40
BOARD_OFFSET = (BOARD_MARGIN, BOARD_MARGIN)

_BOARD_SIDE = DISPLAY_CELL_SIZE * BOARD_CELLS_PER_SIDE + 2 * BOARD_MARGIN
WINDOW_SIZE = (_BOARD_SIDE, _BOARD_SIDE)

# The model/mouse pixel space is defined by the (unchanged) board mapper.
MODEL_CELL_SIZE = GameFactory.CELL_SIZE


def to_model_coords(x: int, y: int) -> tuple[int, int]:
    """
    Translates a window pixel into the model's pixel space so the unchanged
    board mapper resolves the same cell the user clicked on screen.
    """
    model_x = (x - BOARD_MARGIN) * MODEL_CELL_SIZE // DISPLAY_CELL_SIZE
    model_y = (y - BOARD_MARGIN) * MODEL_CELL_SIZE // DISPLAY_CELL_SIZE
    return model_x, model_y


def build_app(image) -> GameApp:
    board = BoardParser().parse(STARTING_BOARD)
    controller, game_engine = GameFactory.create(board)

    library = SpriteLibrary(
        ASSETS_ROOT / PIECE_SET,
        ASSETS_ROOT / BOARD_FILENAME,
        DISPLAY_CELL_SIZE,
        window_size=WINDOW_SIZE,
        board_margin=BOARD_MARGIN,
    )
    clock = AnimationClock()
    provider = AnimationProvider(library, clock, ASSET_STATE_BY_PIECE_STATE)
    renderer = GraphicalRenderer(
        library, DISPLAY_CELL_SIZE, provider.frame_for, BOARD_OFFSET
    )
    snapshot_builder = SnapshotBuilder()

    # The window must exist before the mouse handler is registered, since
    # set_click_handler binds a callback to the window. GameApp.run() opens
    # the window again, which is idempotent and keeps the callback.
    image.open_window()
    mouse_input = MouseInput(
        image, lambda x, y: controller.handle_click(*to_model_coords(x, y))
    )

    return GameApp(
        game_engine,
        controller,
        snapshot_builder,
        renderer,
        image,
        clock,
        mouse_input,
    )


def main() -> None:
    build_app(Img()).run()


if __name__ == "__main__":
    main()
