from kungfu_chess.ui.board_coordinates_layout import (
    BOARD_FILES,
    BoardCoordinatesLayout,
    rank_label,
)
from kungfu_chess.ui.board_coordinates_renderer import BoardCoordinatesRenderer
from kungfu_chess.ui.move_history_panel_layout import MoveHistoryPanelLayout
from kungfu_chess.ui.sprite_library import BOARD_CELLS_PER_SIDE
from kungfu_chess.ui.ui_rect import Rect

SMALL_BOARD_RECT = Rect(120, 80, 240, 240)
SMALL_CELL_SIZE = 30
LARGE_BOARD_RECT = Rect(300, 200, 640, 640)
LARGE_CELL_SIZE = 80
HISTORY_PANEL_SIZE = (220, 600)


class FakeCanvas:
    def __init__(self):
        self.put_text_calls = []

    def put_text(self, text, x, y, font_size, color, thickness):
        self.put_text_calls.append((text, x, y, font_size, color, thickness))


def expected_placements(board_rect: Rect, cell_size: int):
    layout = BoardCoordinatesLayout.from_board(board_rect, cell_size)
    return tuple(
        (placement.text, placement.x, placement.y)
        for placement in (
            layout.top_files
            + layout.bottom_files
            + layout.left_ranks
            + layout.right_ranks
        )
    )


def test_draws_all_file_letters():
    canvas = FakeCanvas()
    renderer = BoardCoordinatesRenderer()

    renderer.draw(canvas, SMALL_BOARD_RECT, SMALL_CELL_SIZE)

    file_labels = [call[0] for call in canvas.put_text_calls if call[0] in BOARD_FILES]
    assert sorted(set(file_labels)) == list(BOARD_FILES)
    assert len(file_labels) == len(BOARD_FILES) * 2


def test_draws_all_rank_numbers():
    canvas = FakeCanvas()
    renderer = BoardCoordinatesRenderer()
    expected_ranks = {str(rank) for rank in range(1, BOARD_CELLS_PER_SIDE + 1)}

    renderer.draw(canvas, SMALL_BOARD_RECT, SMALL_CELL_SIZE)

    rank_labels = [
        call[0]
        for call in canvas.put_text_calls
        if call[0].isdigit()
    ]
    assert sorted(set(rank_labels)) == sorted(expected_ranks)
    assert len(rank_labels) == BOARD_CELLS_PER_SIDE * 2


def test_positions_are_computed_from_board_rect_and_cell_size():
    canvas = FakeCanvas()
    renderer = BoardCoordinatesRenderer()

    renderer.draw(canvas, SMALL_BOARD_RECT, SMALL_CELL_SIZE)

    assert [
        (call[0], call[1], call[2]) for call in canvas.put_text_calls
    ] == list(expected_placements(SMALL_BOARD_RECT, SMALL_CELL_SIZE))


def test_rank_labels_follow_row_index():
    layout = BoardCoordinatesLayout.from_board(SMALL_BOARD_RECT, SMALL_CELL_SIZE)

    assert [placement.text for placement in layout.left_ranks] == [
        rank_label(row) for row in range(BOARD_CELLS_PER_SIDE)
    ]


def test_rendering_scales_when_board_size_changes():
    small_layout = BoardCoordinatesLayout.from_board(
        SMALL_BOARD_RECT,
        SMALL_CELL_SIZE,
    )
    large_layout = BoardCoordinatesLayout.from_board(
        LARGE_BOARD_RECT,
        LARGE_CELL_SIZE,
    )

    assert large_layout.font_size > small_layout.font_size
    assert large_layout.inner_margin > small_layout.inner_margin
    assert small_layout.top_files[0].x != large_layout.top_files[0].x
    assert small_layout.left_ranks[0].y != large_layout.left_ranks[0].y


def test_layout_uses_only_board_rect_and_cell_size():
    first = BoardCoordinatesLayout.from_board(Rect(10, 20, 160, 160), 20)
    second = BoardCoordinatesLayout.from_board(Rect(50, 60, 160, 160), 20)

    assert first.font_size == second.font_size
    assert first.top_files[0].x != second.top_files[0].x
    assert first.top_files[0].y != second.top_files[0].y


def test_top_and_bottom_file_labels_share_horizontal_positions():
    layout = BoardCoordinatesLayout.from_board(SMALL_BOARD_RECT, SMALL_CELL_SIZE)

    assert [placement.x for placement in layout.top_files] == [
        placement.x for placement in layout.bottom_files
    ]


def test_left_and_right_rank_labels_share_vertical_positions():
    layout = BoardCoordinatesLayout.from_board(SMALL_BOARD_RECT, SMALL_CELL_SIZE)

    assert [placement.y for placement in layout.left_ranks] == [
        placement.y for placement in layout.right_ranks
    ]


def test_labels_stay_outside_board_bounds():
    layout = BoardCoordinatesLayout.from_board(SMALL_BOARD_RECT, SMALL_CELL_SIZE)

    for placement in layout.top_files:
        assert placement.y <= SMALL_BOARD_RECT.y

    for placement in layout.bottom_files:
        assert placement.y >= SMALL_BOARD_RECT.bottom

    for placement in layout.left_ranks:
        assert placement.x + 10 <= SMALL_BOARD_RECT.x

    for placement in layout.right_ranks:
        assert placement.x >= SMALL_BOARD_RECT.right


def test_font_size_is_smaller_than_move_history_entry_font():
    coordinates_layout = BoardCoordinatesLayout.from_board(
        SMALL_BOARD_RECT,
        SMALL_CELL_SIZE,
    )
    history_layout = MoveHistoryPanelLayout.from_panel_size(*HISTORY_PANEL_SIZE)

    assert coordinates_layout.font_size < history_layout.entry_font_size
