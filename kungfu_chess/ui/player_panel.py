from kungfu_chess.ui.player_panel_data import PlayerPanelData
from kungfu_chess.ui.player_panel_layout import PlayerPanelLayout
from kungfu_chess.ui.ui_rect import Rect

TEXT_COLOR = (230, 230, 230, 255)
TEXT_THICKNESS = 1


def format_score_line(score: int) -> str:
    return f"Score: {score}"


class PlayerPanel:
    """
    Renders a player name and score inside a provided rectangle.

    The panel is a reusable UI component. It knows only how to draw the
    supplied data within responsive bounds.
    """

    def draw(self, canvas, data: PlayerPanelData, bounds: Rect) -> None:
        layout = PlayerPanelLayout.from_panel_size(bounds.width, bounds.height)
        score_text = format_score_line(data.score)
        name_placement, score_placement = layout.placements(
            bounds,
            data.name,
            score_text,
        )

        for placement in (name_placement, score_placement):
            canvas.put_text(
                placement.text,
                placement.x,
                placement.y,
                placement.font_size,
                TEXT_COLOR,
                TEXT_THICKNESS,
            )
