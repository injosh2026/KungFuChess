import kungfu_chess.ui.composition_root as composition
from kungfu_chess.config.demo_config import STARTING_BOARD
from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.input.mouse_input import MouseInput
from kungfu_chess.io.board_parser import BoardParser
from kungfu_chess.model.position import Position
from kungfu_chess.ui.game_app import GameApp
from kungfu_chess.ui.game_ui_layout import GameUILayout

CANVAS_SIZE = (1000, 800)
PIECE_PIXEL = 50
SELECTED_POSITION = Position(0, 0)


class FakeImage:
    def __init__(self, canvas_size=CANVAS_SIZE):
        self._canvas_size = canvas_size
        self.handler = None
        self.opened = False
        self.img = None

    def open_window(self):
        self.opened = True

    def prime_window(self):
        return None

    def canvas_size(self):
        return self._canvas_size

    def set_click_handler(self, handler):
        self.handler = handler


class FailIfCanvasSizeCalled(FakeImage):
    def canvas_size(self):
        raise AssertionError("canvas_size must not be called during build_app")


def test_build_app_wires_a_game_app_without_opening_window():
    image = FakeImage()

    app = composition.build_app(image)

    assert isinstance(app, GameApp)
    assert image.opened is False
    assert image.handler is None


def test_build_app_does_not_call_canvas_size():
    image = FailIfCanvasSizeCalled()

    composition.build_app(image)


def test_run_attaches_click_handler_after_window_exists():
    image = FakeImage()
    app = composition.build_app(image)

    image.open_window()
    image.prime_window()
    app._mouse_input.attach(image)

    assert image.handler is not None


def test_registered_click_reaches_the_controller():
    board = BoardParser().parse(STARTING_BOARD)
    controller, _, _, _ = GameFactory.create(board)
    image = FakeImage()
    mouse_input = MouseInput(controller.handle_click)

    mouse_input.attach(image)
    image.handler(PIECE_PIXEL, PIECE_PIXEL)

    assert controller.selected_position == SELECTED_POSITION


def test_to_model_coords_maps_display_click_to_same_cell():
    layout = GameUILayout.from_canvas_size(*CANVAS_SIZE)
    board_offset_x, board_offset_y = layout.board_offset
    display_cell = layout.display_cell_size
    model_cell = composition.MODEL_CELL_SIZE
    canvas_size = lambda: CANVAS_SIZE

    for row in range(8):
        for col in range(8):
            display_x = board_offset_x + col * display_cell + display_cell // 2
            display_y = board_offset_y + row * display_cell + display_cell // 2

            model_x, model_y = composition.to_model_coords(
                display_x,
                display_y,
                canvas_size,
            )

            assert (model_x // model_cell, model_y // model_cell) == (col, row)


def test_display_click_over_piece_selects_it_through_the_adapter():
    board = BoardParser().parse(STARTING_BOARD)
    controller, _, _, _ = GameFactory.create(board)
    image = FakeImage()
    layout = GameUILayout.from_canvas_size(*CANVAS_SIZE)
    canvas_size = lambda: CANVAS_SIZE
    mouse_input = MouseInput(
        lambda x, y: controller.handle_click(
            *composition.to_model_coords(x, y, canvas_size),
        ),
    )

    mouse_input.attach(image)
    board_offset_x, board_offset_y = layout.board_offset
    center = board_offset_x + layout.display_cell_size // 2
    image.handler(center, board_offset_y + layout.display_cell_size // 2)

    assert controller.selected_position == SELECTED_POSITION
