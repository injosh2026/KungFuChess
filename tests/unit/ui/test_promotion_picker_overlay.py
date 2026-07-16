from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.ui.promotion_picker_overlay import PromotionPickerOverlay
from kungfu_chess.view.game_snapshot import PromotionSnapshot

WINDOW_SIZE = (800, 800)


class FakeCanvas:
    def __init__(self):
        self.tint_rect_calls = []
        self.draw_rect_calls = []
        self.put_text_calls = []

    def tint_rect(self, x, y, width, height, color, alpha):
        self.tint_rect_calls.append((x, y, width, height, color, alpha))

    def draw_rect(self, x, y, width, height, color, thickness):
        self.draw_rect_calls.append((x, y, width, height, color, thickness))

    def put_text(self, txt, x, y, font_size, color, thickness):
        self.put_text_calls.append((txt, x, y, font_size, color, thickness))


def test_draw_creates_one_button_per_allowed_kind():
    canvas = FakeCanvas()
    overlay = PromotionPickerOverlay(*WINDOW_SIZE)
    allowed = frozenset({PieceKind.QUEEN, PieceKind.ROOK})

    overlay.draw(
        canvas,
        PromotionSnapshot(
            piece_id=1,
            position=object(),
            color=object(),
            allowed_kinds=allowed,
        ),
    )

    assert len(canvas.draw_rect_calls) == 2
    assert {call[0] for call in canvas.put_text_calls} == {"Queen", "Rook"}


def test_pick_choice_returns_clicked_kind():
    overlay = PromotionPickerOverlay(*WINDOW_SIZE)
    allowed = frozenset({PieceKind.QUEEN, PieceKind.KNIGHT})
    _, _, _, _, buttons = overlay._layout(allowed)
    queen_button = next(button for button in buttons if button[0] == PieceKind.QUEEN)
    _, x, y, width, height = queen_button

    chosen = overlay.pick_choice(x + width // 2, y + height // 2, allowed)

    assert chosen == PieceKind.QUEEN
