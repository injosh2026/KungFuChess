from collections.abc import Callable

from kungfu_chess.input.promote_pawn_command import PromotePawnCommand
from kungfu_chess.input.controller import Controller
from kungfu_chess.rules.pawn_end_outcome import PendingPawnPromotion
from kungfu_chess.ui.promotion_picker_overlay import PromotionPickerOverlay


class ClickRouter:
    """
    Routes window clicks to board input or promotion picker input.

    When a pawn promotion is pending, clicks on picker buttons are
    forwarded to the controller. All other clicks go to board handling.
    """

    def __init__(
        self,
        controller: Controller,
        promotion_picker: PromotionPickerOverlay,
        get_pending_promotion: Callable[[], PendingPawnPromotion | None],
        board_click_handler: Callable[[int, int], object],
        canvas_size_provider: Callable[[], tuple[int, int]],
    ):
        self._controller = controller
        self._promotion_picker = promotion_picker
        self._get_pending_promotion = get_pending_promotion
        self._board_click_handler = board_click_handler
        self._canvas_size_provider = canvas_size_provider

    def __call__(self, x: int, y: int):
        pending = self._get_pending_promotion()
        if pending is not None:
            canvas_width, canvas_height = self._canvas_size_provider()
            chosen_kind = self._promotion_picker.pick_choice(
                x,
                y,
                pending.allowed_kinds,
                canvas_width,
                canvas_height,
            )
            if chosen_kind is not None:
                return self._controller.handle_promotion_choice(
                    PromotePawnCommand(pending.piece_id, chosen_kind)
                )

        return self._board_click_handler(x, y)
