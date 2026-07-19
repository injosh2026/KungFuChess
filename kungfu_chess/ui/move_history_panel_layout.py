from dataclasses import dataclass

TEXT_HEIGHT_FACTOR = 22.0
APPROX_CHAR_WIDTH_FACTOR = 10.0

MIN_TITLE_FONT_SIZE = 0.55
MAX_TITLE_FONT_SIZE = 1.1
MIN_ENTRY_FONT_SIZE = 0.45
MAX_ENTRY_FONT_SIZE = 0.95

TITLE_FONT_HEIGHT_RATIO = 0.00125
ENTRY_FONT_HEIGHT_RATIO = 0.00105

TOP_PADDING_RATIO = 0.035
BOTTOM_PADDING_RATIO = 0.02
SIDE_PADDING_RATIO = 0.045
SECTION_SPACING_RATIO = 0.5
ENTRY_SPACING_RATIO = 0.35

MIN_TOP_PADDING = 10
MAX_TOP_PADDING = 28
MIN_BOTTOM_PADDING = 6
MAX_BOTTOM_PADDING = 18
MIN_SIDE_PADDING = 6
MAX_SIDE_PADDING = 18

ELLIPSIS = "..."


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def _clamp_int(value: float, minimum: int, maximum: int) -> int:
    return int(round(_clamp(value, minimum, maximum)))


def approximate_text_width(text: str, font_size: float) -> float:
    return len(text) * font_size * APPROX_CHAR_WIDTH_FACTOR


def fit_text_to_width(text: str, font_size: float, max_width: int) -> str:
    if max_width <= 0:
        return ""

    if approximate_text_width(text, font_size) <= max_width:
        return text

    max_chars = int(max_width / (font_size * APPROX_CHAR_WIDTH_FACTOR))
    if max_chars <= len(ELLIPSIS):
        return ELLIPSIS[:max_chars]

    return text[: max_chars - len(ELLIPSIS)] + ELLIPSIS


@dataclass(frozen=True, slots=True)
class MoveHistoryPanelLayout:
    """
    Responsive layout metrics for a move history side panel.

    All vertical positions are derived from padding, text height, and spacing
    values so future panel sections can reuse the same model.
    """

    top_padding: int
    title_height: float
    section_spacing: float
    line_height: float
    entry_spacing: float
    side_padding: int
    bottom_padding: int
    title_font_size: float
    entry_font_size: float

    @classmethod
    def from_panel_size(
        cls,
        panel_width: int,
        panel_height: int,
    ) -> "MoveHistoryPanelLayout":
        title_font_size = _clamp(
            panel_height * TITLE_FONT_HEIGHT_RATIO,
            MIN_TITLE_FONT_SIZE,
            MAX_TITLE_FONT_SIZE,
        )
        entry_font_size = _clamp(
            panel_height * ENTRY_FONT_HEIGHT_RATIO,
            MIN_ENTRY_FONT_SIZE,
            MAX_ENTRY_FONT_SIZE,
        )

        title_height = title_font_size * TEXT_HEIGHT_FACTOR
        line_height = entry_font_size * TEXT_HEIGHT_FACTOR
        section_spacing = line_height * SECTION_SPACING_RATIO
        entry_spacing = line_height * ENTRY_SPACING_RATIO

        return cls(
            top_padding=_clamp_int(
                panel_height * TOP_PADDING_RATIO,
                MIN_TOP_PADDING,
                MAX_TOP_PADDING,
            ),
            title_height=title_height,
            section_spacing=section_spacing,
            line_height=line_height,
            entry_spacing=entry_spacing,
            side_padding=_clamp_int(
                panel_width * SIDE_PADDING_RATIO,
                MIN_SIDE_PADDING,
                MAX_SIDE_PADDING,
            ),
            bottom_padding=_clamp_int(
                panel_height * BOTTOM_PADDING_RATIO,
                MIN_BOTTOM_PADDING,
                MAX_BOTTOM_PADDING,
            ),
            title_font_size=title_font_size,
            entry_font_size=entry_font_size,
        )

    def title_baseline_y(self, panel_y: int) -> int:
        return panel_y + int(round(self.top_padding + self.title_height))

    def entry_baseline_y(self, panel_y: int, index: int) -> int:
        first_entry_baseline = (
            self.title_baseline_y(panel_y) + self.section_spacing + self.line_height
        )
        return int(
            round(first_entry_baseline + index * (self.line_height + self.entry_spacing))
        )

    def text_x(self, panel_x: int) -> int:
        return panel_x + self.side_padding

    def max_text_width(self, panel_width: int) -> int:
        return max(0, panel_width - 2 * self.side_padding)

    def max_entry_baseline_y(self, panel_y: int, panel_height: int) -> int:
        return panel_y + panel_height - self.bottom_padding
