from dataclasses import dataclass

import cv2

from kungfu_chess.ui.ui_rect import Rect

FONT = cv2.FONT_HERSHEY_SIMPLEX
TEXT_THICKNESS = 1
TEXT_HEIGHT_FACTOR = 22.0

MIN_NAME_FONT_SIZE = 0.32
MAX_NAME_FONT_SIZE = 0.58
MIN_SCORE_FONT_SIZE = 0.55
MAX_SCORE_FONT_SIZE = 1.15

NAME_FONT_HEIGHT_RATIO = 0.0022
SCORE_FONT_HEIGHT_RATIO = 0.0055
NAME_TO_SCORE_FONT_RATIO = 0.58
LINE_SPACING_RATIO = 0.12
VERTICAL_PADDING_RATIO = 0.1


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def _text_size(text: str, font_size: float) -> tuple[int, int]:
    width, height = cv2.getTextSize(text, FONT, font_size, TEXT_THICKNESS)[0]
    return width, height


@dataclass(frozen=True, slots=True)
class TextPlacement:
    text: str
    x: int
    y: int
    font_size: float


@dataclass(frozen=True, slots=True)
class PlayerPanelLayout:
    name_font_size: float
    score_font_size: float
    name_line_height: float
    score_line_height: float
    line_spacing: float
    vertical_padding: int

    @classmethod
    def from_panel_size(cls, panel_width: int, panel_height: int) -> "PlayerPanelLayout":
        score_font_size = _clamp(
            panel_height * SCORE_FONT_HEIGHT_RATIO,
            MIN_SCORE_FONT_SIZE,
            MAX_SCORE_FONT_SIZE,
        )
        name_font_size = _clamp(
            panel_height * NAME_FONT_HEIGHT_RATIO,
            MIN_NAME_FONT_SIZE,
            MAX_NAME_FONT_SIZE,
        )
        name_font_size = min(name_font_size, score_font_size * NAME_TO_SCORE_FONT_RATIO)

        score_line_height = score_font_size * TEXT_HEIGHT_FACTOR
        name_line_height = name_font_size * TEXT_HEIGHT_FACTOR
        line_spacing = score_line_height * LINE_SPACING_RATIO

        return cls(
            name_font_size=name_font_size,
            score_font_size=score_font_size,
            name_line_height=name_line_height,
            score_line_height=score_line_height,
            line_spacing=line_spacing,
            vertical_padding=int(round(panel_height * VERTICAL_PADDING_RATIO)),
        )

    def name_placement(self, bounds: Rect, name: str, score_baseline_y: int) -> TextPlacement:
        text_width, _ = _text_size(name, self.name_font_size)
        x = bounds.x + (bounds.width - text_width) // 2
        y = int(round(score_baseline_y - self.score_line_height - self.line_spacing))
        return TextPlacement(name, x, y, self.name_font_size)

    def score_placement(self, bounds: Rect, score_text: str) -> TextPlacement:
        text_width, _ = _text_size(score_text, self.score_font_size)
        x = bounds.x + (bounds.width - text_width) // 2
        center_y = bounds.y + bounds.height / 2
        y = int(round(center_y + self.score_line_height / 2))
        return TextPlacement(score_text, x, y, self.score_font_size)

    def placements(
        self,
        bounds: Rect,
        name: str,
        score_text: str,
    ) -> tuple[TextPlacement, TextPlacement]:
        score = self.score_placement(bounds, score_text)
        name = self.name_placement(bounds, name, score.y)
        return name, score

    @property
    def text_block_height(self) -> float:
        return self.name_line_height + self.line_spacing + self.score_line_height
