from pathlib import Path

from img import Img
from kungfu_chess.ui.sprite_library import SpriteLibrary

ASSETS_ROOT = Path(__file__).resolve().parents[3] / "assets"
PIECE_SET = "pieces2"
BOARD_FILENAME = "board.png"
CELL_SIZE = 100

DEMO_CODE = "QW"
DEMO_STATE = "idle"
EXPECTED_FRAMES = 5
EXPECTED_FPS = 6

ALL_CODES = [
    "PW", "PB", "RW", "RB", "NW", "NB",
    "BW", "BB", "QW", "QB", "KW", "KB",
]


def make_library() -> SpriteLibrary:
    return SpriteLibrary(
        ASSETS_ROOT / PIECE_SET,
        ASSETS_ROOT / BOARD_FILENAME,
        CELL_SIZE,
        Img,
    )


def test_bundled_board_loads():
    canvas = make_library().background()

    assert canvas.img is not None


def test_bundled_animation_loads_from_project_assets():
    animation = make_library().get_animation(DEMO_CODE, DEMO_STATE)

    assert len(animation.frames) == EXPECTED_FRAMES
    assert animation.fps == EXPECTED_FPS
    assert animation.is_loop is True
    assert all(frame.img is not None for frame in animation.frames)


def test_every_piece_code_has_loadable_idle_animation():
    library = make_library()

    for code in ALL_CODES:
        animation = library.get_animation(code, DEMO_STATE)

        assert len(animation.frames) > 0
        assert all(frame.img is not None for frame in animation.frames)
