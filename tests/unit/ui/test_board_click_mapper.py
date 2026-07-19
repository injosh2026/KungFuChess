from kungfu_chess.config.demo_config import STARTING_BOARD
from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.input.board_mapper import BoardMapper
from kungfu_chess.io.board_parser import BoardParser
from kungfu_chess.model.position import Position
from kungfu_chess.ui import composition_root as composition
from kungfu_chess.ui.board_click_mapper import (
    window_coords_to_model_coords,
    window_coords_to_position,
)
from kungfu_chess.ui.game_ui_layout import GameUILayout, layout_for_canvas_size_provider

MODEL_CELL_SIZE = GameFactory.CELL_SIZE


def layout_with_offset_board():
    return GameUILayout.from_canvas_size(
        900,
        700,
        header_ratio=0.1,
        footer_ratio=0.1,
        sidebar_ratio=0.15,
    )


def cell_center(layout: GameUILayout, row: int, col: int) -> tuple[int, int]:
    board_rect = layout.board_rect
    cell_size = layout.display_cell_size
    x = board_rect.x + col * cell_size + cell_size // 2
    y = board_rect.y + row * cell_size + cell_size // 2
    return x, y


def test_window_coords_to_position_uses_board_rect_offset():
    layout = layout_with_offset_board()

    for row in range(8):
        for col in range(8):
            click_x, click_y = cell_center(layout, row, col)
            assert window_coords_to_position(click_x, click_y, layout) == Position(
                row,
                col,
            )


def test_window_coords_to_model_coords_matches_board_mapper():
    layout = layout_with_offset_board()
    mapper = BoardMapper(MODEL_CELL_SIZE)
    board = BoardParser().parse(STARTING_BOARD)

    for row in range(8):
        for col in range(8):
            click_x, click_y = cell_center(layout, row, col)
            model_x, model_y = window_coords_to_model_coords(
                click_x,
                click_y,
                layout,
                MODEL_CELL_SIZE,
            )
            assert mapper.pixel_to_position(board, model_x, model_y) == Position(
                row,
                col,
            )


def test_to_model_coords_uses_same_layout_as_renderer_bootstrap():
    def failing_provider():
        raise ValueError("unavailable")

    layout = layout_for_canvas_size_provider(failing_provider)
    click_x, click_y = cell_center(layout, 0, 0)

    model_x, model_y = composition.to_model_coords(
        click_x,
        click_y,
        failing_provider,
    )

    assert window_coords_to_model_coords(
        click_x,
        click_y,
        layout,
        MODEL_CELL_SIZE,
    ) == (model_x, model_y)


def test_resize_keeps_input_mapping_for_same_board_cell():
    small = GameUILayout.from_canvas_size(900, 700)
    large = GameUILayout.from_canvas_size(1400, 1000)
    mapper = BoardMapper(MODEL_CELL_SIZE)
    board = BoardParser().parse(STARTING_BOARD)

    for layout in (small, large):
        click_x, click_y = cell_center(layout, 6, 0)
        model_x, model_y = window_coords_to_model_coords(
            click_x,
            click_y,
            layout,
            MODEL_CELL_SIZE,
        )
        assert mapper.pixel_to_position(board, model_x, model_y) == Position(6, 0)
