import examples.demo_ui as demo
from kungfu_chess.ui.animation_clock import AnimationClock
from kungfu_chess.ui.animation_provider import AnimationProvider
from kungfu_chess.ui.graphical_renderer import GraphicalRenderer
from kungfu_chess.ui.promotion_picker_overlay import PromotionPickerOverlay
from kungfu_chess.ui.sprite_library import SpriteLibrary
from kungfu_chess.ui.state_progress_overlay import StateProgressOverlay

BOARD_SIZE = 8
EXPECTED_PIECE_COUNT = 32


class FakeImg:
    def __init__(self):
        self.draws = []

    def draw_on(self, canvas, x, y):
        canvas.draws.append((x, y))


class FakeLibrary:
    def background(self):
        return FakeImg()


class FakeStateProgressOverlay:
    def draw(self, canvas, x, y, cell_size, progress):
        pass


def test_snapshot_has_full_starting_board():
    snapshot = demo.build_snapshot()

    assert snapshot.board_width == BOARD_SIZE
    assert snapshot.board_height == BOARD_SIZE
    assert len(snapshot.pieces) == EXPECTED_PIECE_COUNT


def test_renderer_draws_every_piece_from_snapshot():
    snapshot = demo.build_snapshot()
    requested = []

    def provider(piece):
        requested.append(piece.piece_id)
        return FakeImg()

    canvas = GraphicalRenderer(
        FakeLibrary(),
        demo.CELL_SIZE,
        provider,
        FakeStateProgressOverlay(),
        PromotionPickerOverlay(800, 800),
    ).render(snapshot)

    assert len(requested) == EXPECTED_PIECE_COUNT
    assert len(canvas.draws) == EXPECTED_PIECE_COUNT


def test_full_board_renders_with_bundled_assets():
    library = SpriteLibrary(
        demo.ASSETS_ROOT / demo.PIECE_SET,
        demo.ASSETS_ROOT / demo.BOARD_FILENAME,
        demo.CELL_SIZE,
    )
    provider = AnimationProvider(library, AnimationClock())
    renderer = GraphicalRenderer(
        library,
        demo.CELL_SIZE,
        provider.frame_for,
        StateProgressOverlay(),
        PromotionPickerOverlay(800, 800),
    )

    canvas = renderer.render(demo.build_snapshot())

    assert canvas.img is not None
