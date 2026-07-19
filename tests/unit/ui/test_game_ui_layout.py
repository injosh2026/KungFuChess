from kungfu_chess.ui.game_ui_layout import GameUILayout
from kungfu_chess.ui.ui_rect import Rect


def test_layout_divides_canvas_proportionally():
    layout = GameUILayout.from_canvas_size(1000, 800)

    assert layout.header_rect == Rect(0, 0, 1000, 80)
    assert layout.header_left_rect == Rect(0, 0, 500, 80)
    assert layout.header_right_rect == Rect(500, 0, 500, 80)
    assert layout.footer_rect == Rect(0, 720, 1000, 80)
    assert layout.left_sidebar_rect.y == layout.header_rect.height
    assert layout.left_sidebar_rect.height == 640


def test_layout_reserves_sidebars_and_center_region():
    layout = GameUILayout.from_canvas_size(1000, 800)

    assert layout.left_sidebar_rect == Rect(0, 80, 200, 640)
    assert layout.right_sidebar_rect == Rect(800, 80, 200, 640)
    assert layout.board_region_rect == Rect(200, 80, 600, 640)


def test_board_is_square_and_centered_in_board_region():
    layout = GameUILayout.from_canvas_size(1000, 800)

    assert layout.board_rect.width == layout.board_rect.height
    region = layout.board_region_rect
    assert layout.board_rect.x == region.x + (region.width - layout.board_rect.width) // 2
    assert layout.board_rect.y == region.y + (region.height - layout.board_rect.height) // 2


def test_board_side_uses_smaller_board_region_dimension():
    layout = GameUILayout.from_canvas_size(1000, 800)

    assert layout.board_rect.width == min(
        layout.board_region_rect.width,
        layout.board_region_rect.height,
    )


def test_board_does_not_overlap_sidebars():
    layout = GameUILayout.from_canvas_size(1000, 800)

    assert layout.board_rect.right <= layout.right_sidebar_rect.x
    assert layout.board_rect.x >= layout.left_sidebar_rect.right


def test_display_cell_size_scales_with_canvas():
    small = GameUILayout.from_canvas_size(800, 600)
    large = GameUILayout.from_canvas_size(1400, 1000)

    assert small.display_cell_size < large.display_cell_size


def test_layout_without_chrome_fills_entire_canvas():
    layout = GameUILayout.from_canvas_size(
        800,
        800,
        header_ratio=0.0,
        footer_ratio=0.0,
        sidebar_ratio=0.0,
    )

    assert layout.board_rect == Rect(0, 0, 800, 800)
    assert layout.board_offset == (0, 0)
    assert layout.display_cell_size == 100


def test_layout_recomputes_from_different_canvas_sizes():
    small = GameUILayout.from_canvas_size(800, 600)
    large = GameUILayout.from_canvas_size(1600, 1200)

    assert small.canvas_size != large.canvas_size
    assert small.left_sidebar_rect.width < large.left_sidebar_rect.width
    assert small.board_rect.width < large.board_rect.width
