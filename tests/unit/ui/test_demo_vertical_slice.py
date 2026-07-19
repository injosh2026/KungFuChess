import examples.demo_ui as demo
from kungfu_chess.ui.animation_clock import AnimationClock
from kungfu_chess.ui.animation_provider import AnimationProvider
from kungfu_chess.ui.board_coordinates_renderer import BoardCoordinatesRenderer
from kungfu_chess.ui.player_panel import PlayerPanel
from kungfu_chess.ui.player_panel_data import PlayerPanelConfig
from kungfu_chess.ui.graphical_renderer import GraphicalRenderer
from kungfu_chess.ui.move_history_panel import MoveHistoryPanel
from kungfu_chess.ui.promotion_picker_overlay import PromotionPickerOverlay
from kungfu_chess.ui.sprite_library import SpriteLibrary
from kungfu_chess.ui.state_progress_overlay import StateProgressOverlay

CANVAS_SIZE = (1000, 800)
BOARD_SIZE = 8
EXPECTED_PIECE_COUNT = 32


class FakeImg:
    def __init__(self):
        self.draws = []

    def draw_on(self, canvas, x, y):
        canvas.draws.append((x, y))

    def put_text(self, text, x, y, font_size, color, thickness):
        return None


class FakeLibrary:
    def set_display_cell_size(self, cell_size):
        pass

    def background(self, canvas_width, canvas_height, board_origin=None):
        return FakeImg()


class FakeStateProgressOverlay:
    def draw(self, canvas, x, y, cell_size, progress):
        pass


class FakeMoveHistoryPanel:
    def draw(self, canvas, move_history, bounds):
        pass


def test_snapshot_has_full_starting_board():
    snapshot = demo.build_snapshot(lambda: CANVAS_SIZE)

    assert snapshot.board_width == BOARD_SIZE
    assert snapshot.board_height == BOARD_SIZE
    assert len(snapshot.pieces) == EXPECTED_PIECE_COUNT


def test_renderer_draws_every_piece_from_snapshot():
    snapshot = demo.build_snapshot(lambda: CANVAS_SIZE)
    requested = []

    def provider(piece):
        requested.append(piece.piece_id)
        return FakeImg()

    canvas = GraphicalRenderer(
        FakeLibrary(),
        lambda: CANVAS_SIZE,
        provider,
        FakeStateProgressOverlay(),
        PromotionPickerOverlay(),
        FakeMoveHistoryPanel(),
        FakeMoveHistoryPanel(),
        BoardCoordinatesRenderer(),
        PlayerPanel(),
        PlayerPanelConfig("White", "W"),
        PlayerPanelConfig("Black", "B"),
    ).render(snapshot)

    assert len(requested) == EXPECTED_PIECE_COUNT
    assert len(canvas.draws) == EXPECTED_PIECE_COUNT


def test_full_board_renders_with_bundled_assets():
    from kungfu_chess.ui.game_ui_layout import GameUILayout

    layout = GameUILayout.from_canvas_size(*CANVAS_SIZE)
    library = SpriteLibrary(
        demo.ASSETS_ROOT / demo.PIECE_SET,
        demo.ASSETS_ROOT / demo.BOARD_FILENAME,
        layout.display_cell_size,
    )
    provider = AnimationProvider(library, AnimationClock())
    renderer = GraphicalRenderer(
        library,
        lambda: CANVAS_SIZE,
        provider.frame_for,
        StateProgressOverlay(),
        PromotionPickerOverlay(),
        MoveHistoryPanel("White"),
        MoveHistoryPanel("Black"),
        BoardCoordinatesRenderer(),
        PlayerPanel(),
        PlayerPanelConfig("White", "W"),
        PlayerPanelConfig("Black", "B"),
    )

    canvas = renderer.render(demo.build_snapshot(lambda: CANVAS_SIZE))

    assert canvas.img is not None
