import json

from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position
from kungfu_chess.ui.graphical_renderer import GraphicalRenderer
from kungfu_chess.ui.piece_code import piece_code
from kungfu_chess.ui.sprite_animator import SpriteAnimator
from kungfu_chess.ui.sprite_library import SpriteLibrary
from kungfu_chess.view.game_snapshot import GameSnapshot, PieceSnapshot

CELL_SIZE = 100
STATE = "move"
FPS = 10
# 10 fps -> 100 ms per frame, so 100 ms selects the second frame (index 1).
ELAPSED_MS = 100


class FakeImage:
    def __init__(self):
        self.read_calls = []
        self.draw_on_calls = []

    def read(self, path, size=None, keep_aspect=False):
        self.read_calls.append((path, size, keep_aspect))
        return self

    def draw_on(self, other, x, y):
        self.draw_on_calls.append((other, x, y))


class FakeImageFactory:
    def __call__(self):
        return FakeImage()


def build_assets(tmp_path, code):
    board_path = tmp_path / "board.png"
    board_path.touch()

    sprites_dir = tmp_path / "pieces1" / code / "states" / STATE / "sprites"
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

    return tmp_path / "pieces1", board_path


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
    )


def test_full_ui_chain_draws_the_animated_frame(tmp_path):
    code = piece_code(PieceKind.QUEEN, Color.WHITE)
    pieces_root, board_path = build_assets(tmp_path, code)

    library = SpriteLibrary(pieces_root, board_path, CELL_SIZE, FakeImageFactory())

    def frame_provider(piece):
        animation = library.get_animation(
            piece_code(piece.kind, piece.color), STATE
        )
        return SpriteAnimator(animation).frame_at(ELAPSED_MS)

    renderer = GraphicalRenderer(library, CELL_SIZE, frame_provider)

    canvas = renderer.render(make_snapshot())

    # SpriteLibrary returns a valid AnimationData with 3 loaded frames.
    animation = library.get_animation(code, STATE)
    assert len(animation.frames) == 3
    assert animation.fps == FPS

    # SpriteAnimator selects the expected Img frame, which the renderer draws.
    expected_frame = SpriteAnimator(animation).frame_at(ELAPSED_MS)
    assert expected_frame is animation.frames[1]
    assert expected_frame.draw_on_calls == [(canvas, 3 * CELL_SIZE, 2 * CELL_SIZE)]
