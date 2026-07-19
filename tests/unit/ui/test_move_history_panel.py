from kungfu_chess.ui.move_history_panel import (
    MoveHistoryPanel,
    filter_history_by_piece_code_suffix,
    format_elapsed_time,
    format_move_history_line,
)
from kungfu_chess.ui.move_history_panel_layout import (
    MoveHistoryPanelLayout,
    fit_text_to_width,
)
from kungfu_chess.ui.ui_rect import Rect
from kungfu_chess.view.move_history_entry import MoveHistoryEntry


class FakeCanvas:
    def __init__(self):
        self.put_text_calls = []

    def put_text(self, text, x, y, font_size, color, thickness):
        self.put_text_calls.append((text, x, y, font_size, color, thickness))


def test_format_elapsed_time():
    assert format_elapsed_time(83000) == "00:01:23"


def test_format_move_history_line():
    entry = MoveHistoryEntry(
        elapsed_time_ms=83000,
        piece_code="PW",
        piece_name="pawn",
        from_square="e2",
        to_square="e4",
    )

    assert format_move_history_line(entry) == "00:01:23 Pawn e2 → e4"


def test_filter_history_by_piece_code_suffix():
    history = (
        MoveHistoryEntry(
            elapsed_time_ms=1000,
            piece_code="PW",
            piece_name="pawn",
            from_square="e2",
            to_square="e4",
        ),
        MoveHistoryEntry(
            elapsed_time_ms=1500,
            piece_code="NB",
            piece_name="knight",
            from_square="b8",
            to_square="c6",
        ),
    )

    assert filter_history_by_piece_code_suffix(history, "W") == (history[0],)
    assert filter_history_by_piece_code_suffix(history, "B") == (history[1],)


def test_fit_text_to_width_truncates_long_lines():
    text = "00:00:18 Pawn e7 → e5"

    fitted = fit_text_to_width(text, font_size=0.75, max_width=120)

    assert fitted.endswith("...")
    assert len(fitted) < len(text)


def test_layout_scales_font_sizes_with_panel_height():
    small = MoveHistoryPanelLayout.from_panel_size(180, 300)
    large = MoveHistoryPanelLayout.from_panel_size(180, 640)

    assert small.title_font_size < large.title_font_size
    assert small.entry_font_size < large.entry_font_size


def test_layout_derives_vertical_positions_from_metrics():
    bounds = Rect(0, 80, 200, 640)
    layout = MoveHistoryPanelLayout.from_panel_size(bounds.width, bounds.height)

    title_y = layout.title_baseline_y(bounds.y)
    first_entry_y = layout.entry_baseline_y(bounds.y, 0)
    second_entry_y = layout.entry_baseline_y(bounds.y, 1)

    assert title_y >= bounds.y + layout.top_padding
    assert first_entry_y > title_y + layout.section_spacing
    assert second_entry_y - first_entry_y >= layout.line_height + layout.entry_spacing * 0.9


def test_panel_draws_title_and_entries_inside_bounds():
    canvas = FakeCanvas()
    bounds = Rect(0, 80, 240, 640)
    panel = MoveHistoryPanel("White")
    history = (
        MoveHistoryEntry(
            elapsed_time_ms=1000,
            piece_code="PW",
            piece_name="pawn",
            from_square="e2",
            to_square="e4",
        ),
        MoveHistoryEntry(
            elapsed_time_ms=2500,
            piece_code="QW",
            piece_name="queen",
            from_square="d1",
            to_square="h5",
        ),
    )
    layout = MoveHistoryPanelLayout.from_panel_size(bounds.width, bounds.height)

    panel.draw(canvas, history, bounds)

    assert canvas.put_text_calls[0] == (
        "White",
        layout.text_x(bounds.x),
        layout.title_baseline_y(bounds.y),
        layout.title_font_size,
        MoveHistoryPanel.TEXT_COLOR,
        MoveHistoryPanel.TEXT_THICKNESS,
    )
    assert canvas.put_text_calls[1][0] == "00:00:01 Pawn e2 → e4"
    assert canvas.put_text_calls[2][0] == "00:00:02 Queen d1 → h5"


def test_panel_title_has_top_padding_instead_of_edge_baseline():
    canvas = FakeCanvas()
    bounds = Rect(0, 80, 200, 640)
    panel = MoveHistoryPanel("White")
    layout = MoveHistoryPanelLayout.from_panel_size(bounds.width, bounds.height)

    panel.draw(canvas, (), bounds)

    _, _, title_y, title_font_size, _, _ = canvas.put_text_calls[0]

    assert title_y >= bounds.y + layout.top_padding + title_font_size * 10


def test_panel_entry_spacing_is_readable():
    canvas = FakeCanvas()
    bounds = Rect(0, 80, 200, 640)
    panel = MoveHistoryPanel("White")
    history = (
        MoveHistoryEntry(
            elapsed_time_ms=1000,
            piece_code="PW",
            piece_name="pawn",
            from_square="e2",
            to_square="e4",
        ),
        MoveHistoryEntry(
            elapsed_time_ms=2500,
            piece_code="QW",
            piece_name="queen",
            from_square="d1",
            to_square="h5",
        ),
    )
    layout = MoveHistoryPanelLayout.from_panel_size(bounds.width, bounds.height)

    panel.draw(canvas, history, bounds)

    first_entry_y = canvas.put_text_calls[1][2]
    second_entry_y = canvas.put_text_calls[2][2]

    assert second_entry_y - first_entry_y >= layout.line_height + layout.entry_spacing * 0.9


def test_panel_clips_long_entries_to_panel_width():
    canvas = FakeCanvas()
    bounds = Rect(0, 80, 120, 640)
    panel = MoveHistoryPanel("White")
    history = (
        MoveHistoryEntry(
            elapsed_time_ms=18000,
            piece_code="PW",
            piece_name="pawn",
            from_square="e7",
            to_square="e5",
        ),
    )

    panel.draw(canvas, history, bounds)

    rendered_line = canvas.put_text_calls[1][0]
    assert rendered_line.endswith("...")
    assert canvas.put_text_calls[1][1] <= bounds.x + bounds.width
