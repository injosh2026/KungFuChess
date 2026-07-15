from typing import Callable

from img import Img
from kungfu_chess.model.position import Position
from kungfu_chess.ui.sprite_library import SpriteLibrary
from kungfu_chess.view.game_snapshot import GameSnapshot, PieceSnapshot
from kungfu_chess.view.renderer import Renderer

GAME_OVER_TEXT = "GAME OVER"
OVERLAY_FONT_SIZE = 2.0
OVERLAY_TEXT_COLOR = (255, 255, 255, 255)
OVERLAY_TEXT_THICKNESS = 3

SELECTION_BORDER_COLOR = (0, 255, 255, 255)
SELECTION_BORDER_THICKNESS = 6
NO_OFFSET = (0, 0)


class GraphicalRenderer(Renderer):
    """
    Draws a game snapshot onto the board background using ready frames.

    GraphicalRenderer consumes only immutable GameSnapshot objects and
    never accesses the mutable game state. For each piece it asks an
    injected frame provider for a ready-to-draw frame; it does not select
    states or advance animation itself.

    Draw order: background, pieces, selection, overlays. The composed
    canvas is returned; presenting it is left to the caller.
    """

    def __init__(
        self,
        sprite_library: SpriteLibrary,
        cell_size: int,
        frame_provider: Callable[[PieceSnapshot], Img],
        board_offset: tuple[int, int] = NO_OFFSET,
    ):
        """
        Creates a graphical renderer.

        Args:
            sprite_library:
                Source of the board background canvas.

            cell_size:
                Size in pixels of a single board cell.

            frame_provider:
                Callable that returns the ready frame to draw for a
                given piece snapshot.

            board_offset:
                Pixel (x, y) offset of the board's top-left corner inside
                the canvas, used to leave a margin around the board.
        """
        self._sprite_library = sprite_library
        self._cell_size = cell_size
        self._frame_provider = frame_provider
        self._board_offset = board_offset

    def render(self, snapshot: GameSnapshot) -> Img:
        canvas = self._sprite_library.background()

        self._draw_pieces(snapshot, canvas)

        if snapshot.selected_cell is not None:
            self._draw_selection(snapshot.selected_cell, canvas)

        if snapshot.game_over:
            self._draw_game_over(canvas)

        return canvas

    def _draw_pieces(self, snapshot: GameSnapshot, canvas: Img) -> None:
        for piece in snapshot.pieces:
            frame = self._frame_provider(piece)

            if piece.visual_position is not None:
                x, y = piece.visual_position
            else:
                x, y = self._cell_to_pixel(piece)

            frame.draw_on(canvas, int(x), int(y))

    def _draw_selection(self, cell: Position, canvas: Img) -> None:
        x, y = self._cell_origin(cell.row, cell.col)
        canvas.draw_rect(
            x,
            y,
            self._cell_size,
            self._cell_size,
            SELECTION_BORDER_COLOR,
            SELECTION_BORDER_THICKNESS,
        )

    def _draw_game_over(self, canvas: Img) -> None:
        canvas.put_text(
            GAME_OVER_TEXT,
            self._cell_size,
            self._cell_size,
            OVERLAY_FONT_SIZE,
            OVERLAY_TEXT_COLOR,
            OVERLAY_TEXT_THICKNESS,
        )

    def _cell_to_pixel(self, piece: PieceSnapshot) -> tuple[int, int]:
        return self._cell_origin(piece.position.row, piece.position.col)

    def _cell_origin(self, row: int, col: int) -> tuple[int, int]:
        offset_x, offset_y = self._board_offset
        x = offset_x + col * self._cell_size
        y = offset_y + row * self._cell_size
        return x, y
