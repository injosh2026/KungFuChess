import json

from kungfu_chess.ui.sprite_library import SpriteLibrary

CELL_SIZE = 100
CODE = "QW"
STATE = "move"


class FakeImage:
    def __init__(self):
        self.read_calls = []

    def read(self, path, size=None, keep_aspect=False):
        self.read_calls.append((path, size, keep_aspect))
        return self


class FakeImageFactory:
    def __init__(self):
        self.instances = []

    def __call__(self):
        image = FakeImage()
        self.instances.append(image)
        return image


def build_assets(tmp_path, frame_numbers, config):
    board_path = tmp_path / "board.png"
    board_path.touch()

    state_dir = tmp_path / "pieces1" / CODE / "states" / STATE
    sprites_dir = state_dir / "sprites"
    sprites_dir.mkdir(parents=True)

    for number in frame_numbers:
        (sprites_dir / f"{number}.png").touch()

    (state_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")

    return tmp_path / "pieces1", board_path


DEFAULT_CONFIG = {
    "physics": {"speed_m_per_sec": 1.5, "next_state_when_finished": "long_rest"},
    "graphics": {"frames_per_sec": 12, "is_loop": True},
}


def make_library(tmp_path, frame_numbers, config=DEFAULT_CONFIG):
    pieces_root, board_path = build_assets(tmp_path, frame_numbers, config)
    factory = FakeImageFactory()
    library = SpriteLibrary(pieces_root, board_path, CELL_SIZE, factory)
    return library, factory


def test_get_animation_reads_config_values(tmp_path):
    library, _ = make_library(tmp_path, [1, 2, 3])

    animation = library.get_animation(CODE, STATE)

    assert animation.fps == 12
    assert animation.is_loop is True
    assert animation.next_state_when_finished == "long_rest"
    assert animation.speed_m_per_sec == 1.5


def test_get_animation_loads_all_frames(tmp_path):
    library, _ = make_library(tmp_path, [1, 2, 3, 4, 5])

    animation = library.get_animation(CODE, STATE)

    assert len(animation.frames) == 5


def test_frames_are_ordered_numerically(tmp_path):
    library, _ = make_library(tmp_path, [10, 2, 1])

    animation = library.get_animation(CODE, STATE)

    loaded_names = [frame.read_calls[0][0] for frame in animation.frames]
    assert loaded_names[0].endswith("1.png")
    assert loaded_names[1].endswith("2.png")
    assert loaded_names[2].endswith("10.png")


def test_frames_are_resized_to_cell(tmp_path):
    library, _ = make_library(tmp_path, [1])

    animation = library.get_animation(CODE, STATE)

    _, size, keep_aspect = animation.frames[0].read_calls[0]
    assert size == (CELL_SIZE, CELL_SIZE)
    assert keep_aspect is True


def test_get_animation_is_cached(tmp_path):
    library, factory = make_library(tmp_path, [1, 2])

    first = library.get_animation(CODE, STATE)
    second = library.get_animation(CODE, STATE)

    assert first is second
    assert len(factory.instances) == 2


def test_background_is_fresh_per_call(tmp_path):
    library, factory = make_library(tmp_path, [1])

    first = library.background()
    second = library.background()

    assert first is not second
    assert first.read_calls[0][1] is None
