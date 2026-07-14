import examples.game_app_demo as composition
from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.input.mouse_input import MouseInput
from kungfu_chess.io.board_parser import BoardParser
from kungfu_chess.model.position import Position
from kungfu_chess.ui.game_app import GameApp

PIECE_PIXEL = 50
SELECTED_POSITION = Position(0, 0)


class FakeImage:
    def __init__(self):
        self.handler = None
        self.opened = False

    def open_window(self):
        self.opened = True

    def set_click_handler(self, handler):
        self.handler = handler


def test_build_app_wires_a_game_app_and_registers_click_handler():
    image = FakeImage()

    app = composition.build_app(image)

    assert isinstance(app, GameApp)
    assert image.opened is True
    assert image.handler is not None


def test_registered_click_reaches_the_controller():
    board = BoardParser().parse(composition.STARTING_BOARD)
    controller, _ = GameFactory.create(board)
    image = FakeImage()

    MouseInput(image, controller.handle_click)
    image.handler(PIECE_PIXEL, PIECE_PIXEL)

    assert controller.selected_position == SELECTED_POSITION


def test_to_model_coords_maps_display_click_to_same_cell():
    margin = composition.BOARD_MARGIN
    display_cell = composition.DISPLAY_CELL_SIZE
    model_cell = composition.MODEL_CELL_SIZE

    for row in range(8):
        for col in range(8):
            display_x = margin + col * display_cell + display_cell // 2
            display_y = margin + row * display_cell + display_cell // 2

            model_x, model_y = composition.to_model_coords(display_x, display_y)

            assert (model_x // model_cell, model_y // model_cell) == (col, row)


def test_display_click_over_piece_selects_it_through_the_adapter():
    board = BoardParser().parse(composition.STARTING_BOARD)
    controller, _ = GameFactory.create(board)
    image = FakeImage()

    MouseInput(
        image,
        lambda x, y: controller.handle_click(*composition.to_model_coords(x, y)),
    )
    center = composition.BOARD_MARGIN + composition.DISPLAY_CELL_SIZE // 2
    image.handler(center, center)

    assert controller.selected_position == SELECTED_POSITION
