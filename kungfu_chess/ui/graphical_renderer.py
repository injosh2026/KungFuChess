from typing import Callable

from img import Img
from kungfu_chess.model.position import Position
from kungfu_chess.ui.promotion_picker_overlay import PromotionPickerOverlay
from kungfu_chess.ui.sprite_library import SpriteLibrary
from kungfu_chess.ui.state_progress_overlay import StateProgressOverlay
from kungfu_chess.view.game_snapshot import GameSnapshot, PieceSnapshot
from kungfu_chess.view.renderer import Renderer

GAME_OVER_TEXT = "GAME OVER"
OVERLAY_FONT_SIZE = 2.0
OVERLAY_TEXT_COLOR = (255, 255, 255, 255)
OVERLAY_TEXT_THICKNESS = 3

SELECTION_BORDER_COLOR = (0, 255, 255, 255)
SELECTION_BORDER_THICKNESS = 6
NO_OFFSET = (0, 0)

LEGAL_MOVE_ALPHA = 0.25


class GraphicalRenderer(Renderer):
    """
    Draws a game snapshot onto the board background using ready frames.

    GraphicalRenderer consumes only immutable GameSnapshot objects and
    never accesses the mutable game state. For each piece it asks an
    injected frame provider for a ready-to-draw frame; it does not select
    states or advance animation itself.

    Draw order: background, legal moves, state progress overlays, pieces,
    selection, game over. Overlays are drawn beneath piece sprites so the
    piece remains visible while the cell fill drains over time.
    """

    def __init__(
        self,
        sprite_library: SpriteLibrary,
        cell_size: int,
        frame_provider: Callable[[PieceSnapshot], Img],
        state_progress_overlay: StateProgressOverlay,
        promotion_picker_overlay: PromotionPickerOverlay,
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

            state_progress_overlay:
                Draws a visual effect when a piece snapshot carries
                timed-state progress.

            board_offset:
                Pixel (x, y) offset of the board's top-left corner inside
                the canvas, used to leave a margin around the board.
        """
        self._sprite_library = sprite_library
        self._cell_size = cell_size
        self._frame_provider = frame_provider
        self._state_progress_overlay = state_progress_overlay
        self._promotion_picker_overlay = promotion_picker_overlay
        self._board_offset = board_offset

    def render(self, snapshot: GameSnapshot) -> Img:
        canvas = self._sprite_library.background()

        self._draw_legal_moves(snapshot.legal_moves, canvas)

        self._draw_state_progress_overlays(snapshot, canvas)

        self._draw_pieces(snapshot, canvas)

        if snapshot.selected_cell is not None:
            self._draw_selection(snapshot.selected_cell, canvas)

        if snapshot.game_over:
            self._draw_game_over(canvas)

        if snapshot.pending_promotion is not None:
            self._promotion_picker_overlay.draw(canvas, snapshot.pending_promotion)

        return canvas

    def _draw_pieces(self, snapshot: GameSnapshot, canvas: Img) -> None:
        for piece in snapshot.pieces:
            frame = self._frame_provider(piece)
            x, y = self._piece_draw_position(piece)
            frame.draw_on(canvas, int(x), int(y))

    def _draw_state_progress_overlays(
        self,
        snapshot: GameSnapshot,
        canvas: Img,
    ) -> None:
        for piece in snapshot.pieces:
            if piece.state_progress is None:
                continue

            x, y = self._piece_draw_position(piece)
            self._state_progress_overlay.draw(
                canvas,
                int(x),
                int(y),
                self._cell_size,
                piece.state_progress,
            )

    def _piece_draw_position(self, piece: PieceSnapshot) -> tuple[float, float]:
        if piece.visual_position is not None:
            return piece.visual_position
        return self._cell_to_pixel(piece)

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

    def _draw_legal_moves(self, moves: set[Position], canvas: Img, ) -> None:

        for move in moves:
            x, y = self._cell_origin(
                move.row,
                move.col,
            )

            canvas.tint_rect(
                x,
                y,
                self._cell_size,
                self._cell_size,
                color=(0, 255, 255),
                alpha=LEGAL_MOVE_ALPHA,
            )
