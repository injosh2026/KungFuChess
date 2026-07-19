import json

from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position
from kungfu_chess.ui.board_coordinates_renderer import BoardCoordinatesRenderer
from kungfu_chess.ui.player_panel import PlayerPanel
from kungfu_chess.ui.player_panel_data import PlayerPanelConfig
from kungfu_chess.ui.graphical_renderer import GraphicalRenderer
from kungfu_chess.ui.piece_code import piece_code
from kungfu_chess.ui.sprite_animator import SpriteAnimator
from kungfu_chess.ui.sprite_library import SpriteLibrary
from kungfu_chess.ui.game_ui_layout import GameUILayout
from kungfu_chess.ui.move_history_panel import MoveHistoryPanel
from kungfu_chess.ui.promotion_picker_overlay import PromotionPickerOverlay
from kungfu_chess.ui.state_progress_overlay import StateProgressOverlay
from kungfu_chess.view.game_snapshot import GameSnapshot, PieceSnapshot

CANVAS_SIZE = (1000, 800)
STATE = "move"
FPS = 10
ELAPSED_MS = 100


class FakeImage:
    def __init__(self):
        self.read_calls = []
        self.draw_on_calls = []
        self.put_text_calls = []

    def read(self, path, size=None, keep_aspect=False):
        self.read_calls.append((path, size, keep_aspect))
        return self

    def draw_on(self, other, x, y):
        self.draw_on_calls.append((other, x, y))

    def put_text(self, text, x, y, font_size, color, thickness):
        self.put_text_calls.append((text, x, y, font_size, color, thickness))

    def create_blank(self, width, height, color):
        return self


class FakeImageFactory:
    def __call__(self):
        return FakeImage()


def build_assets(tmp_path, code):
    board_path = tmp_path / "board.png"
    board_path.touch()

    sprites_dir = tmp_path / "pieces2" / code / "states" / STATE / "sprites"
    sprites_dir.mkdir(parents=True)
    for number in (1, 2, 3):
        (sprites_dir / f"{number}.png").touch()

    config = {
        "physics": {"speed_m_per_sec": 1.5, "next_state_when_finished": "long_rest"},
        "graphics": {"frames_per_sec": FPS, "is_loop": True},
    }
    (sprites_dir.parent / "config.json").write_text(
        json.dumps(config), encoding="utf-8"
    )

    long_rest_dir = tmp_path / "pieces2" / code / "states" / "long_rest"

    long_rest_dir.mkdir(parents=True)

    (long_rest_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")

    return tmp_path / "pieces2", board_path


def make_snapshot():
    piece = PieceSnapshot(
        piece_id=1,
        kind=PieceKind.QUEEN,
        color=Color.WHITE,
        position=Position(2, 3),
        state=PieceState.IDLE,
    )
    return GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=[piece],
        selected_cell=None,
        game_over=False,
        legal_moves=set(),
    )


def test_full_ui_chain_draws_the_animated_frame(tmp_path):
    code = piece_code(PieceKind.QUEEN, Color.WHITE)
    pieces_root, board_path = build_assets(tmp_path, code)
    layout = GameUILayout.from_canvas_size(*CANVAS_SIZE)
    library = SpriteLibrary(
        pieces_root,
        board_path,
        layout.display_cell_size,
        FakeImageFactory(),
    )

    def frame_provider(piece):
        animation = library.get_animation(piece_code(piece.kind, piece.color), STATE)
        return SpriteAnimator(animation).frame_at(ELAPSED_MS)

    renderer = GraphicalRenderer(
        library,
        lambda: CANVAS_SIZE,
        frame_provider,
        StateProgressOverlay(),
        PromotionPickerOverlay(),
        MoveHistoryPanel("White"),
        MoveHistoryPanel("Black"),
        BoardCoordinatesRenderer(),
        PlayerPanel(),
        PlayerPanelConfig("White", "W"),
        PlayerPanelConfig("Black", "B"),
    )

    canvas = renderer.render(make_snapshot())

    animation = library.get_animation(code, STATE)
    assert len(animation.frames) == 3
    assert animation.fps == FPS

    expected_frame = SpriteAnimator(animation).frame_at(ELAPSED_MS)
    assert expected_frame is animation.frames[1]
    board_offset_x, board_offset_y = layout.board_offset
    expected_x = board_offset_x + 3 * layout.display_cell_size
    expected_y = board_offset_y + 2 * layout.display_cell_size
    assert expected_frame.draw_on_calls == [(canvas, expected_x, expected_y)]
