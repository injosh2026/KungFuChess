from img import Img
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.view.game_snapshot import PromotionSnapshot

PANEL_PADDING = 12
BUTTON_WIDTH = 160
BUTTON_HEIGHT = 36
BUTTON_GAP = 8
PANEL_BACKGROUND_ALPHA = 0.75
PANEL_BACKGROUND_COLOR = (40, 40, 40)
BUTTON_BORDER_COLOR = (255, 255, 255, 255)
BUTTON_BORDER_THICKNESS = 2
LABEL_COLOR = (255, 255, 255, 255)
LABEL_FONT_SIZE = 0.6
LABEL_THICKNESS = 2
LABEL_Y_OFFSET = 24


class PromotionPickerOverlay:
    """
    Draws a simple promotion choice panel and maps clicks to piece kinds.

    The overlay uses allowed kinds from the snapshot only. It does not
    validate choices or modify game state.
    """

    def draw(
        self,
        canvas: Img,
        promotion: PromotionSnapshot,
        canvas_width: int,
        canvas_height: int,
    ) -> None:
        panel_x, panel_y, panel_width, panel_height, buttons = self._layout(
            promotion.allowed_kinds,
            canvas_width,
            canvas_height,
        )

        canvas.tint_rect(
            panel_x,
            panel_y,
            panel_width,
            panel_height,
            color=PANEL_BACKGROUND_COLOR,
            alpha=PANEL_BACKGROUND_ALPHA,
        )

        for kind, x, y, width, height in buttons:
            canvas.draw_rect(
                x,
                y,
                width,
                height,
                BUTTON_BORDER_COLOR,
                BUTTON_BORDER_THICKNESS,
            )
            canvas.put_text(
                _label_for_kind(kind),
                x + 12,
                y + LABEL_Y_OFFSET,
                LABEL_FONT_SIZE,
                LABEL_COLOR,
                LABEL_THICKNESS,
            )

    def pick_choice(
        self,
        x: int,
        y: int,
        allowed_kinds: frozenset[PieceKind],
        canvas_width: int,
        canvas_height: int,
    ) -> PieceKind | None:
        _, _, _, _, buttons = self._layout(
            allowed_kinds,
            canvas_width,
            canvas_height,
        )

        for kind, button_x, button_y, width, height in buttons:
            if (
                button_x <= x < button_x + width
                and button_y <= y < button_y + height
            ):
                return kind

        return None

    def _layout(
        self,
        allowed_kinds: frozenset[PieceKind],
        canvas_width: int,
        canvas_height: int,
    ) -> tuple[int, int, int, int, list[tuple[PieceKind, int, int, int, int]]]:
        kinds = sorted(allowed_kinds, key=lambda kind: kind.value)
        total_button_height = (
            len(kinds) * BUTTON_HEIGHT + max(len(kinds) - 1, 0) * BUTTON_GAP
        )
        panel_width = BUTTON_WIDTH + 2 * PANEL_PADDING
        panel_height = total_button_height + 2 * PANEL_PADDING
        panel_x = (canvas_width - panel_width) // 2
        panel_y = (canvas_height - panel_height) // 2

        buttons = []
        button_y = panel_y + PANEL_PADDING
        button_x = panel_x + PANEL_PADDING

        for kind in kinds:
            buttons.append((kind, button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT))
            button_y += BUTTON_HEIGHT + BUTTON_GAP

        return panel_x, panel_y, panel_width, panel_height, buttons


def _label_for_kind(kind: PieceKind) -> str:
    return kind.value.capitalize()
