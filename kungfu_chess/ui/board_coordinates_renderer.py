from kungfu_chess.ui.board_coordinates_layout import BoardCoordinatesLayout
from kungfu_chess.ui.ui_rect import Rect

TEXT_COLOR = (220, 220, 220, 255)


class BoardCoordinatesRenderer:
    """
    Draws chess board file letters and rank numbers around the board rectangle.

    This component is rendering-only. It uses the current board rectangle and
    cell size to place labels responsively every frame.
    """

    def draw(self, canvas, board_rect: Rect, cell_size: int) -> None:
        layout = BoardCoordinatesLayout.from_board(board_rect, cell_size)

        for placement in (
            layout.top_files
            + layout.bottom_files
            + layout.left_ranks
            + layout.right_ranks
        ):
            canvas.put_text(
                placement.text,
                placement.x,
                placement.y,
                layout.font_size,
                TEXT_COLOR,
                layout.text_thickness,
            )
