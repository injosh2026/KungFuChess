from img import Img

# Google Translate–style purple (Material Deep Purple 500).
OVERLAY_COLOR = (103, 58, 183)
OVERLAY_ALPHA = 0.82


class StateProgressOverlay:
    """
    Draws a timed-state visual effect from normalized progress alone.

    The filled area shrinks vertically from top to bottom as progress
    advances, like sand draining in an hourglass. The overlay does not
    know piece states, config, or engine timing.
    """

    def draw(
        self,
        canvas: Img,
        x: int,
        y: int,
        cell_size: int,
        progress: float,
    ) -> None:
        if progress >= 1.0:
            return

        remaining = 1.0 - progress
        if remaining <= 0.0:
            return

        fill_height = round(cell_size * remaining)
        if fill_height <= 0:
            return

        fill_y = y + (cell_size - fill_height)

        canvas.tint_rect(
            x,
            fill_y,
            cell_size,
            fill_height,
            color=OVERLAY_COLOR,
            alpha=OVERLAY_ALPHA,
        )
