from kungfu_chess.ui.move_history_panel_layout import (
    MoveHistoryPanelLayout,
    fit_text_to_width,
)
from kungfu_chess.ui.ui_rect import Rect
from kungfu_chess.view.move_history_entry import MoveHistoryEntry


def format_elapsed_time(elapsed_time_ms: int) -> str:
    total_seconds = elapsed_time_ms // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def format_move_history_line(entry: MoveHistoryEntry) -> str:
    return (
        f"{format_elapsed_time(entry.elapsed_time_ms)} "
        f"{entry.piece_name.capitalize()} "
        f"{entry.from_square} → {entry.to_square}"
    )


def filter_history_by_piece_code_suffix(
    move_history: tuple[MoveHistoryEntry, ...],
    suffix: str,
) -> tuple[MoveHistoryEntry, ...]:
    return tuple(
        entry for entry in move_history if entry.piece_code.endswith(suffix)
    )


class MoveHistoryPanel:
    """
    Renders the move history list from snapshot data.

    The panel is an independent UI component. It reads only immutable
    history entries already copied into GameSnapshot.
    """

    TEXT_COLOR = (230, 230, 230, 255)
    TEXT_THICKNESS = 1

    def __init__(self, title: str):
        self._title = title

    @property
    def title(self) -> str:
        return self._title

    def draw(
        self,
        canvas,
        move_history: tuple[MoveHistoryEntry, ...],
        bounds: Rect,
    ) -> None:
        layout = MoveHistoryPanelLayout.from_panel_size(bounds.width, bounds.height)
        text_x = layout.text_x(bounds.x)
        max_text_width = layout.max_text_width(bounds.width)
        max_y = layout.max_entry_baseline_y(bounds.y, bounds.height)

        canvas.put_text(
            fit_text_to_width(self._title, layout.title_font_size, max_text_width),
            text_x,
            layout.title_baseline_y(bounds.y),
            layout.title_font_size,
            self.TEXT_COLOR,
            self.TEXT_THICKNESS,
        )

        for index, entry in enumerate(move_history):
            entry_y = layout.entry_baseline_y(bounds.y, index)
            if entry_y > max_y:
                break

            canvas.put_text(
                fit_text_to_width(
                    format_move_history_line(entry),
                    layout.entry_font_size,
                    max_text_width,
                ),
                text_x,
                entry_y,
                layout.entry_font_size,
                self.TEXT_COLOR,
                self.TEXT_THICKNESS,
            )
