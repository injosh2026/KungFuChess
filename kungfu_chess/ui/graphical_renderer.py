from collections.abc import Callable

from img import Img
from kungfu_chess.model.position import Position
from kungfu_chess.ui.board_coordinates_renderer import BoardCoordinatesRenderer
from kungfu_chess.ui.game_ui_layout import BOOTSTRAP_VIEWPORT, GameUILayout, layout_for_canvas_size_provider
from kungfu_chess.ui.move_history_panel import (
    MoveHistoryPanel,
    filter_history_by_piece_code_suffix,
)
from kungfu_chess.ui.player_panel import PlayerPanel
from kungfu_chess.ui.player_panel_data import PlayerPanelConfig, PlayerPanelData
from kungfu_chess.ui.promotion_picker_overlay import PromotionPickerOverlay
from kungfu_chess.ui.sprite_library import SpriteLibrary
from kungfu_chess.ui.state_progress_overlay import StateProgressOverlay
from kungfu_chess.view.game_snapshot import GameSnapshot, PieceSnapshot
from kungfu_chess.view.runtime_role import RuntimeRole
from kungfu_chess.view.renderer import Renderer

GAME_OVER_TEXT = "GAME OVER"
OVERLAY_FONT_SIZE = 2.0
OVERLAY_TEXT_COLOR = (255, 255, 255, 255)
OVERLAY_TEXT_THICKNESS = 3

SELECTION_BORDER_COLOR = (0, 255, 255, 255)
SELECTION_BORDER_THICKNESS = 6

LEGAL_MOVE_ALPHA = 0.25


class GraphicalRenderer(Renderer):
    """
    Draws a game snapshot onto the board background using ready frames.

    GraphicalRenderer consumes only immutable GameSnapshot objects and
    never accesses the mutable game state. For each piece it asks an
    injected frame provider for a ready-to-draw frame; it does not select
    states or advance animation itself.

    Layout is recalculated every frame from the current canvas size. When the
    window size is not yet available from OpenCV, a bootstrap viewport is used
    for that frame only; after the first present, the real window size is used.
    """

    def __init__(
        self,
        sprite_library: SpriteLibrary,
        canvas_size_provider: Callable[[], tuple[int, int]],
        frame_provider: Callable[[PieceSnapshot], Img],
        state_progress_overlay: StateProgressOverlay,
        promotion_picker_overlay: PromotionPickerOverlay,
        white_history_panel: MoveHistoryPanel,
        black_history_panel: MoveHistoryPanel,
        board_coordinates_renderer: BoardCoordinatesRenderer,
        player_panel: PlayerPanel,
        left_player_panel: PlayerPanelConfig,
        right_player_panel: PlayerPanelConfig,
    ):
        self._sprite_library = sprite_library
        self._canvas_size_provider = canvas_size_provider
        self._frame_provider = frame_provider
        self._state_progress_overlay = state_progress_overlay
        self._promotion_picker_overlay = promotion_picker_overlay
        self._white_history_panel = white_history_panel
        self._black_history_panel = black_history_panel
        self._board_coordinates_renderer = board_coordinates_renderer
        self._player_panel = player_panel
        self._left_player_panel = left_player_panel
        self._right_player_panel = right_player_panel
        self._layout = GameUILayout.from_canvas_size(*BOOTSTRAP_VIEWPORT)
        self._cell_size = self._layout.display_cell_size

    @property
    def layout(self) -> GameUILayout:
        return self._layout

    def _resolve_canvas_size(self) -> tuple[int, int]:
        try:
            return self._canvas_size_provider()
        except ValueError:
            return BOOTSTRAP_VIEWPORT

    def render(self, snapshot: GameSnapshot) -> Img:
        layout = layout_for_canvas_size_provider(self._canvas_size_provider)
        canvas_width, canvas_height = layout.canvas_size
        self._layout = layout
        self._cell_size = layout.display_cell_size
        self._sprite_library.set_display_cell_size(layout.display_cell_size)

        canvas = self._sprite_library.background(
            canvas_width,
            canvas_height,
            layout.board_offset,
        )

        self._player_panel.draw(
            canvas,
            PlayerPanelData(
                self._left_player_panel.name,
                snapshot.player_scores.get(self._left_player_panel.player_id, 0),
            ),
            layout.header_left_rect,
        )
        self._player_panel.draw(
            canvas,
            PlayerPanelData(
                self._right_player_panel.name,
                snapshot.player_scores.get(self._right_player_panel.player_id, 0),
            ),
            layout.header_right_rect,
        )

        self._board_coordinates_renderer.draw(
            canvas,
            layout.board_rect,
            layout.display_cell_size,
        )

        self._draw_legal_moves(snapshot.legal_moves, canvas)

        self._draw_state_progress_overlays(snapshot, canvas)

        self._draw_pieces(snapshot, canvas)

        if snapshot.selected_cell is not None:
            self._draw_selection(snapshot.selected_cell, canvas)

        if snapshot.game_over:
            self._draw_game_over(canvas)

        if snapshot.pending_promotion is not None:
            self._promotion_picker_overlay.draw(
                canvas,
                snapshot.pending_promotion,
                canvas_width,
                canvas_height,
            )

        white_history = filter_history_by_piece_code_suffix(
            snapshot.move_history,
            "W",
        )
        black_history = filter_history_by_piece_code_suffix(
            snapshot.move_history,
            "B",
        )
        self._white_history_panel.draw(
            canvas,
            white_history,
            layout.left_sidebar_rect,
        )
        self._black_history_panel.draw(
            canvas,
            black_history,
            layout.right_sidebar_rect,
        )

        return canvas

    def _draw_pieces(self, snapshot: GameSnapshot, canvas: Img) -> None:
        for piece in snapshot.pieces:
            frame = self._frame_provider(piece)
            x, y = self._sprite_draw_position(piece, frame)
            frame.draw_on(canvas, int(x), int(y))

    def _draw_state_progress_overlays(
        self,
        snapshot: GameSnapshot,
        canvas: Img,
    ) -> None:
        for piece in snapshot.pieces:
            recovery_progress = piece.runtime_progress.get(RuntimeRole.RECOVERY)
            if recovery_progress is None:
                continue

            x, y = self._cell_to_pixel(piece)
            self._state_progress_overlay.draw(
                canvas,
                int(x),
                int(y),
                self._cell_size,
                recovery_progress,
            )

    def _sprite_draw_position(
        self,
        piece: PieceSnapshot,
        frame: Img,
    ) -> tuple[float, float]:
        if piece.visual_position is not None:
            return self._visual_center_to_canvas_origin(
                piece.visual_position,
                frame,
            )
        return self._cell_to_pixel(piece)

    def _visual_center_to_canvas_origin(
        self,
        board_local_center: tuple[float, float],
        frame: Img,
    ) -> tuple[float, float]:
        sprite_width, sprite_height = self._frame_size(frame)
        offset_x, offset_y = self._layout.board_offset
        center_x, center_y = board_local_center
        return (
            offset_x + center_x - sprite_width / 2,
            offset_y + center_y - sprite_height / 2,
        )

    def _frame_size(self, frame: Img) -> tuple[int, int]:
        if frame.img is not None:
            height, width = frame.img.shape[:2]
            return width, height
        return self._cell_size, self._cell_size

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
        board_x, board_y = self._layout.board_offset
        canvas.put_text(
            GAME_OVER_TEXT,
            board_x + self._cell_size,
            board_y + self._cell_size,
            OVERLAY_FONT_SIZE,
            OVERLAY_TEXT_COLOR,
            OVERLAY_TEXT_THICKNESS,
        )

    def _cell_to_pixel(self, piece: PieceSnapshot) -> tuple[int, int]:
        return self._cell_origin(piece.position.row, piece.position.col)

    def _cell_origin(self, row: int, col: int) -> tuple[int, int]:
        offset_x, offset_y = self._layout.board_offset
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
