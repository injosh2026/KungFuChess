from kungfu_chess.ui.state_progress_overlay import (
    OVERLAY_ALPHA,
    OVERLAY_COLOR,
    StateProgressOverlay,
)

CELL_SIZE = 100


class FakeImage:
    def __init__(self):
        self.tint_rect_calls = []

    def tint_rect(self, x, y, width, height, color, alpha):
        self.tint_rect_calls.append((x, y, width, height, color, alpha))


def test_progress_zero_fills_entire_cell():
    canvas = FakeImage()
    overlay = StateProgressOverlay()

    overlay.draw(canvas, 10, 20, CELL_SIZE, 0.0)

    assert canvas.tint_rect_calls == [
        (10, 20, CELL_SIZE, CELL_SIZE, OVERLAY_COLOR, OVERLAY_ALPHA),
    ]


def test_progress_half_fills_bottom_half_of_cell():
    canvas = FakeImage()
    overlay = StateProgressOverlay()

    overlay.draw(canvas, 0, 0, CELL_SIZE, 0.5)

    assert canvas.tint_rect_calls == [
        (0, CELL_SIZE // 2, CELL_SIZE, CELL_SIZE // 2, OVERLAY_COLOR, OVERLAY_ALPHA),
    ]


def test_progress_ninety_percent_leaves_ten_percent_fill_at_bottom():
    canvas = FakeImage()
    overlay = StateProgressOverlay()

    overlay.draw(canvas, 0, 0, CELL_SIZE, 0.9)

    assert canvas.tint_rect_calls == [
        (0, 90, CELL_SIZE, 10, OVERLAY_COLOR, OVERLAY_ALPHA),
    ]


def test_progress_one_does_not_draw_overlay():
    canvas = FakeImage()
    overlay = StateProgressOverlay()

    overlay.draw(canvas, 0, 0, CELL_SIZE, 1.0)

    assert canvas.tint_rect_calls == []
