from dataclasses import dataclass

import cv2

from kungfu_chess.ui.sprite_library import BOARD_CELLS_PER_SIDE
from kungfu_chess.ui.ui_rect import Rect

FONT = cv2.FONT_HERSHEY_SIMPLEX
TEXT_THICKNESS = 1

MIN_FONT_SIZE = 0.35
MAX_FONT_SIZE = 0.70
FONT_SIZE_CELL_RATIO = 0.006

MIN_INNER_MARGIN = 4
MAX_INNER_MARGIN = 24
INNER_MARGIN_CELL_RATIO = 0.12

BOARD_FILES = tuple("abcdefgh")


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def _clamp_int(value: float, minimum: int, maximum: int) -> int:
    return int(round(_clamp(value, minimum, maximum)))


def rank_label(row: int) -> str:
    return str(BOARD_CELLS_PER_SIDE - row)


def _text_size(text: str, font_size: float) -> tuple[int, int, int]:
    (width, height), baseline = cv2.getTextSize(
        text,
        FONT,
        font_size,
        TEXT_THICKNESS,
    )
    return width, height, baseline


@dataclass(frozen=True, slots=True)
class LabelPlacement:
    text: str
    x: int
    y: int


@dataclass(frozen=True, slots=True)
class BoardCoordinatesLayout:
    font_size: float
    inner_margin: int
    text_thickness: int
    top_files: tuple[LabelPlacement, ...]
    bottom_files: tuple[LabelPlacement, ...]
    left_ranks: tuple[LabelPlacement, ...]
    right_ranks: tuple[LabelPlacement, ...]

    @classmethod
    def from_board(cls, board_rect: Rect, cell_size: int) -> "BoardCoordinatesLayout":
        font_size = _clamp(
            cell_size * FONT_SIZE_CELL_RATIO,
            MIN_FONT_SIZE,
            MAX_FONT_SIZE,
        )
        inner_margin = _clamp_int(
            cell_size * INNER_MARGIN_CELL_RATIO,
            MIN_INNER_MARGIN,
            MAX_INNER_MARGIN,
        )

        _, sample_height, _ = _text_size("8", font_size)

        top_files = tuple(
            cls._file_label(board_rect, cell_size, font_size, inner_margin, file, "top")
            for file in BOARD_FILES
        )
        bottom_files = tuple(
            cls._file_label(
                board_rect,
                cell_size,
                font_size,
                inner_margin,
                file,
                "bottom",
                sample_height,
            )
            for file in BOARD_FILES
        )
        left_ranks = tuple(
            cls._rank_label(
                board_rect,
                cell_size,
                font_size,
                inner_margin,
                row,
                "left",
            )
            for row in range(BOARD_CELLS_PER_SIDE)
        )
        right_ranks = tuple(
            cls._rank_label(
                board_rect,
                cell_size,
                font_size,
                inner_margin,
                row,
                "right",
            )
            for row in range(BOARD_CELLS_PER_SIDE)
        )

        return cls(
            font_size=font_size,
            inner_margin=inner_margin,
            text_thickness=TEXT_THICKNESS,
            top_files=top_files,
            bottom_files=bottom_files,
            left_ranks=left_ranks,
            right_ranks=right_ranks,
        )

    @staticmethod
    def _file_label(
        board_rect: Rect,
        cell_size: int,
        font_size: float,
        inner_margin: int,
        file: str,
        edge: str,
        text_height: int = 0,
    ) -> LabelPlacement:
        text_width, measured_height, _ = _text_size(file, font_size)
        if text_height == 0:
            text_height = measured_height

        col = ord(file) - ord("a")
        cell_center_x = board_rect.x + col * cell_size + cell_size // 2
        x = cell_center_x - text_width // 2

        if edge == "top":
            y = board_rect.y - inner_margin
        else:
            y = board_rect.bottom + inner_margin + text_height

        return LabelPlacement(file, x, y)

    @staticmethod
    def _rank_label(
        board_rect: Rect,
        cell_size: int,
        font_size: float,
        inner_margin: int,
        row: int,
        edge: str,
    ) -> LabelPlacement:
        text = rank_label(row)
        text_width, text_height, _ = _text_size(text, font_size)
        row_center_y = board_rect.y + row * cell_size + cell_size // 2
        y = row_center_y + text_height // 2

        if edge == "left":
            x = board_rect.x - inner_margin - text_width
        else:
            x = board_rect.right + inner_margin

        return LabelPlacement(text, x, y)
