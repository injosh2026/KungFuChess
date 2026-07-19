from dataclasses import dataclass

from collections.abc import Callable

from kungfu_chess.ui.sprite_library import BOARD_CELLS_PER_SIDE
from kungfu_chess.ui.ui_rect import Rect

HEADER_RATIO = 0.10
FOOTER_RATIO = 0.10
SIDEBAR_RATIO = 0.20
BOOTSTRAP_VIEWPORT = (1000, 800)

@dataclass(frozen=True, slots=True)
class GameUILayout:
    """
    Responsive layout calculated from the current canvas size.

    Input: canvas width and height for the frame being rendered.
    Output: all UI rectangles for that frame.
    """

    canvas_size: tuple[int, int]
    header_rect: Rect
    header_left_rect: Rect
    header_right_rect: Rect
    footer_rect: Rect
    left_sidebar_rect: Rect
    right_sidebar_rect: Rect
    board_region_rect: Rect
    board_rect: Rect
    display_cell_size: int

    @property
    def canvas_width(self) -> int:
        return self.canvas_size[0]

    @property
    def canvas_height(self) -> int:
        return self.canvas_size[1]

    @property
    def board_offset(self) -> tuple[int, int]:
        return (self.board_rect.x, self.board_rect.y)

    @property
    def board_margin(self) -> int:
        return 0

    @property
    def board_side(self) -> int:
        return self.board_rect.width

    @property
    def window_size(self) -> tuple[int, int]:
        return self.canvas_size

    @property
    def history_panel_width(self) -> int:
        return self.left_sidebar_rect.width

    @property
    def left_history_panel_x(self) -> int:
        return self.left_sidebar_rect.x

    @property
    def right_history_panel_x(self) -> int:
        return self.right_sidebar_rect.x

    @property
    def history_panel_height(self) -> int:
        return self.left_sidebar_rect.height

    @classmethod
    def from_canvas_size(
        cls,
        canvas_width: int,
        canvas_height: int,
        *,
        header_ratio: float = HEADER_RATIO,
        footer_ratio: float = FOOTER_RATIO,
        sidebar_ratio: float = SIDEBAR_RATIO,
    ) -> "GameUILayout":
        header_height = int(round(canvas_height * header_ratio))
        footer_height = int(round(canvas_height * footer_ratio))
        content_y = header_height
        content_height = canvas_height - header_height - footer_height

        left_width = int(round(canvas_width * sidebar_ratio))
        right_width = int(round(canvas_width * sidebar_ratio))
        center_width = canvas_width - left_width - right_width
        center_x = left_width

        header_rect = Rect(0, 0, canvas_width, header_height)
        header_left_width = canvas_width // 2
        header_left_rect = Rect(0, 0, header_left_width, header_height)
        header_right_rect = Rect(
            header_left_width,
            0,
            canvas_width - header_left_width,
            header_height,
        )
        footer_rect = Rect(
            0,
            canvas_height - footer_height,
            canvas_width,
            footer_height,
        )
        left_sidebar_rect = Rect(0, content_y, left_width, content_height)
        right_sidebar_rect = Rect(
            canvas_width - right_width,
            content_y,
            right_width,
            content_height,
        )
        board_region_rect = Rect(center_x, content_y, center_width, content_height)

        board_side = min(board_region_rect.width, board_region_rect.height)
        display_cell_size = board_side // BOARD_CELLS_PER_SIDE
        board_side = display_cell_size * BOARD_CELLS_PER_SIDE

        board_x = board_region_rect.x + (board_region_rect.width - board_side) // 2
        board_y = board_region_rect.y + (board_region_rect.height - board_side) // 2
        board_rect = Rect(board_x, board_y, board_side, board_side)

        return cls(
            canvas_size=(canvas_width, canvas_height),
            header_rect=header_rect,
            header_left_rect=header_left_rect,
            header_right_rect=header_right_rect,
            footer_rect=footer_rect,
            left_sidebar_rect=left_sidebar_rect,
            right_sidebar_rect=right_sidebar_rect,
            board_region_rect=board_region_rect,
            board_rect=board_rect,
            display_cell_size=display_cell_size,
        )


def layout_for_canvas_size_provider(
    canvas_size_provider: Callable[[], tuple[int, int]],
) -> "GameUILayout":
    try:
        canvas_width, canvas_height = canvas_size_provider()
    except ValueError:
        canvas_width, canvas_height = BOOTSTRAP_VIEWPORT

    return GameUILayout.from_canvas_size(canvas_width, canvas_height)
