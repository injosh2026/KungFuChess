import cv2

from kungfu_chess.ui.game_ui_layout import GameUILayout
from kungfu_chess.ui.player_panel import PlayerPanel, format_score_line
from kungfu_chess.ui.player_panel_data import PlayerPanelData
from kungfu_chess.ui.player_panel_layout import PlayerPanelLayout
from kungfu_chess.ui.ui_rect import Rect

SMALL_BOUNDS = Rect(0, 0, 300, 60)
LARGE_BOUNDS = Rect(0, 0, 600, 200)
PLAYER_DATA = PlayerPanelData("White", 0)
FONT = cv2.FONT_HERSHEY_SIMPLEX


class FakeCanvas:
    def __init__(self):
        self.put_text_calls = []

    def put_text(self, text, x, y, font_size, color, thickness):
        self.put_text_calls.append((text, x, y, font_size, color, thickness))


def text_width(text: str, font_size: float) -> int:
    return cv2.getTextSize(text, FONT, font_size, 1)[0][0]


def test_player_panel_renders_name():
    canvas = FakeCanvas()
    panel = PlayerPanel()

    panel.draw(canvas, PLAYER_DATA, SMALL_BOUNDS)

    assert canvas.put_text_calls[0][0] == "White"


def test_player_panel_renders_score():
    canvas = FakeCanvas()
    panel = PlayerPanel()

    panel.draw(canvas, PLAYER_DATA, SMALL_BOUNDS)

    assert canvas.put_text_calls[1][0] == format_score_line(0)


def test_player_panel_renders_custom_name_and_score():
    canvas = FakeCanvas()
    panel = PlayerPanel()
    data = PlayerPanelData("Alice", 15)

    panel.draw(canvas, data, SMALL_BOUNDS)

    assert canvas.put_text_calls[0][0] == "Alice"
    assert canvas.put_text_calls[1][0] == "Score: 15"


def test_layout_scales_font_sizes_with_panel_height():
    small = PlayerPanelLayout.from_panel_size(SMALL_BOUNDS.width, SMALL_BOUNDS.height)
    large = PlayerPanelLayout.from_panel_size(LARGE_BOUNDS.width, LARGE_BOUNDS.height)

    assert small.name_font_size < large.name_font_size
    assert small.score_font_size < large.score_font_size
    assert small.score_font_size > small.name_font_size
    assert large.score_font_size > large.name_font_size


def test_score_font_is_larger_than_name_font():
    layout = PlayerPanelLayout.from_panel_size(SMALL_BOUNDS.width, SMALL_BOUNDS.height)

    assert layout.score_font_size > layout.name_font_size


def test_panel_text_is_centered_horizontally_in_rect():
    canvas = FakeCanvas()
    panel = PlayerPanel()
    bounds = Rect(40, 10, 320, 70)

    panel.draw(canvas, PLAYER_DATA, bounds)

    layout = PlayerPanelLayout.from_panel_size(bounds.width, bounds.height)
    name_placement, score_placement = layout.placements(
        bounds,
        PLAYER_DATA.name,
        format_score_line(PLAYER_DATA.score),
    )

    assert canvas.put_text_calls[0][1:4] == (
        name_placement.x,
        name_placement.y,
        name_placement.font_size,
    )
    assert canvas.put_text_calls[1][1:4] == (
        score_placement.x,
        score_placement.y,
        score_placement.font_size,
    )
    assert canvas.put_text_calls[0][1] == bounds.x + (
        bounds.width - text_width(PLAYER_DATA.name, layout.name_font_size)
    ) // 2
    assert canvas.put_text_calls[1][1] == bounds.x + (
        bounds.width - text_width(format_score_line(PLAYER_DATA.score), layout.score_font_size)
    ) // 2


def test_panel_text_is_vertically_centered_in_rect():
    bounds = Rect(40, 10, 320, 70)
    layout = PlayerPanelLayout.from_panel_size(bounds.width, bounds.height)
    name_placement, score_placement = layout.placements(
        bounds,
        PLAYER_DATA.name,
        format_score_line(PLAYER_DATA.score),
    )

    score_center_y = score_placement.y - layout.score_line_height / 2
    panel_center_y = bounds.y + bounds.height / 2

    assert abs(score_center_y - panel_center_y) <= 1
    assert name_placement.y < score_placement.y
    assert name_placement.y - layout.name_line_height >= bounds.y + layout.vertical_padding
    assert score_placement.y <= bounds.bottom - layout.vertical_padding


def test_resize_updates_layout_without_breaking_panel_content():
    canvas = FakeCanvas()
    panel = PlayerPanel()

    panel.draw(canvas, PLAYER_DATA, SMALL_BOUNDS)
    small_fonts = [call[3] for call in canvas.put_text_calls]

    canvas.put_text_calls.clear()
    panel.draw(canvas, PLAYER_DATA, LARGE_BOUNDS)
    large_fonts = [call[3] for call in canvas.put_text_calls]

    assert small_fonts[0] < large_fonts[0]
    assert small_fonts[1] < large_fonts[1]
    assert [call[0] for call in canvas.put_text_calls] == ["White", "Score: 0"]


def test_header_layout_scales_panel_regions_with_canvas_width():
    small = GameUILayout.from_canvas_size(800, 600)
    large = GameUILayout.from_canvas_size(1600, 1200)

    assert small.header_left_rect.width < large.header_left_rect.width
    assert small.header_right_rect.width < large.header_right_rect.width
    assert small.header_left_rect.height < large.header_left_rect.height


def test_header_layout_provides_left_and_right_panel_regions():
    layout = GameUILayout.from_canvas_size(1000, 800)

    assert layout.header_left_rect == Rect(0, 0, 500, 80)
    assert layout.header_right_rect == Rect(500, 0, 500, 80)
    assert layout.header_left_rect.y == layout.header_rect.y
    assert layout.header_right_rect.bottom == layout.header_rect.bottom
    assert layout.header_left_rect.right == layout.header_right_rect.x
