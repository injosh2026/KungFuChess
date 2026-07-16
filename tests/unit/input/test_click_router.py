from kungfu_chess.input.click_router import ClickRouter
from kungfu_chess.input.promote_pawn_command import PromotePawnCommand
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.rules.chess_pawn_end_handler import ChessPawnEndHandler
from kungfu_chess.rules.pawn_end_outcome import PendingPawnPromotion
from kungfu_chess.ui.promotion_picker_overlay import PromotionPickerOverlay

WINDOW_SIZE = (800, 800)


class FakeController:
    def __init__(self):
        self.promotion_commands = []
        self.board_clicks = []

    def handle_promotion_choice(self, command):
        self.promotion_commands.append(command)
        return "promotion_result"

    def handle_click(self, x, y):
        self.board_clicks.append((x, y))
        return None


def create_router(pending=None):
    controller = FakeController()
    picker = PromotionPickerOverlay(*WINDOW_SIZE)
    router = ClickRouter(
        controller,
        picker,
        lambda: pending,
        lambda x, y: controller.handle_click(x, y),
    )
    return router, controller, picker


def _click_center_of_kind(picker, allowed_kinds, kind):
    _, _, _, _, buttons = picker._layout(allowed_kinds)
    for button_kind, x, y, width, height in buttons:
        if button_kind == kind:
            return x + width // 2, y + height // 2
    raise AssertionError(f"button not found for {kind}")


def test_click_router_forwards_queen_choice_to_controller():
    pending = PendingPawnPromotion(
        piece_id=5,
        allowed_kinds=ChessPawnEndHandler.PROMOTION_KINDS,
    )
    router, controller, picker = create_router(pending)
    x, y = _click_center_of_kind(
        picker,
        pending.allowed_kinds,
        PieceKind.QUEEN,
    )

    result = router(x, y)

    assert result == "promotion_result"
    assert controller.promotion_commands == [
        PromotePawnCommand(piece_id=5, chosen_kind=PieceKind.QUEEN)
    ]
    assert controller.board_clicks == []


def test_click_router_forwards_knight_choice_to_controller():
    pending = PendingPawnPromotion(
        piece_id=5,
        allowed_kinds=ChessPawnEndHandler.PROMOTION_KINDS,
    )
    router, controller, picker = create_router(pending)
    x, y = _click_center_of_kind(
        picker,
        pending.allowed_kinds,
        PieceKind.KNIGHT,
    )

    router(x, y)

    assert controller.promotion_commands == [
        PromotePawnCommand(piece_id=5, chosen_kind=PieceKind.KNIGHT)
    ]


def test_click_router_forwards_board_click_when_no_pending_promotion():
    router, controller, picker = create_router(None)

    router(120, 140)

    assert controller.board_clicks == [(120, 140)]
    assert controller.promotion_commands == []


def test_click_router_forwards_board_click_outside_picker_buttons():
    pending = PendingPawnPromotion(
        piece_id=5,
        allowed_kinds=ChessPawnEndHandler.PROMOTION_KINDS,
    )
    router, controller, _ = create_router(pending)

    router(10, 10)

    assert controller.board_clicks == [(10, 10)]
    assert controller.promotion_commands == []
