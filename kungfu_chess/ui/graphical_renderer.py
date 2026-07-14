from typing import Callable

from img import Img
from kungfu_chess.ui.sprite_library import SpriteLibrary
from kungfu_chess.view.game_snapshot import GameSnapshot, PieceSnapshot
from kungfu_chess.view.renderer import Renderer

GAME_OVER_TEXT = "GAME OVER"
OVERLAY_FONT_SIZE = 2.0
OVERLAY_TEXT_COLOR = (255, 255, 255, 255)
OVERLAY_TEXT_THICKNESS = 3


class GraphicalRenderer(Renderer):
    """
    Draws a game snapshot onto the board background using ready frames.

    GraphicalRenderer consumes only immutable GameSnapshot objects and
    never accesses the mutable game state. For each piece it asks an
    injected frame provider for a ready-to-draw frame; it does not select
    states or advance animation itself.

    Draw order: background, pieces, overlays. The composed canvas is
    returned; presenting it is left to the caller.
    """

    def __init__(
        self,
        sprite_library: SpriteLibrary,
        cell_size: int,
        frame_provider: Callable[[PieceSnapshot], Img],
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
        """
        self._sprite_library = sprite_library
        self._cell_size = cell_size
        self._frame_provider = frame_provider

    def render(self, snapshot: GameSnapshot) -> Img:
        canvas = self._sprite_library.background()

        self._draw_pieces(snapshot, canvas)

        # TODO: render selection highlight for snapshot.selected_cell

        if snapshot.game_over:
            self._draw_game_over(canvas)

        return canvas

    def _draw_pieces(self, snapshot: GameSnapshot, canvas: Img) -> None:
        for piece in snapshot.pieces:
            frame = self._frame_provider(piece)
            x, y = self._cell_to_pixel(piece)
            frame.draw_on(canvas, x, y)

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
        x = piece.position.col * self._cell_size
        y = piece.position.row * self._cell_size
        return x, y
