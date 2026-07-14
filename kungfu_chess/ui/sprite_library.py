import json
from pathlib import Path
from typing import Callable

from img import Img
from kungfu_chess.ui.animation_data import AnimationData

STATES_DIRNAME = "states"
SPRITES_DIRNAME = "sprites"
CONFIG_FILENAME = "config.json"
SPRITE_EXTENSION = ".png"

CONFIG_PHYSICS = "physics"
CONFIG_GRAPHICS = "graphics"
CONFIG_SPEED = "speed_m_per_sec"
CONFIG_NEXT_STATE = "next_state_when_finished"
CONFIG_FPS = "frames_per_sec"
CONFIG_IS_LOOP = "is_loop"


class SpriteLibrary:
    """
    Loads and caches piece animation assets.

    SpriteLibrary is the only place that reads image files and config
    files. For a given piece code and state it loads all frames and the
    state's config.json, and caches the result. The board background is
    loaded fresh on every request, because it is used as a render canvas
    and drawing mutates it.

    It does not decide which state is active, does not advance animation,
    and contains no rendering logic.
    """

    def __init__(
        self,
        pieces_root: str | Path,
        board_path: str | Path,
        cell_size: int,
        image_factory: Callable[[], Img] = Img,
        sprite_extension: str = SPRITE_EXTENSION,
    ):
        """
        Creates a sprite library.

        Args:
            pieces_root:
                Path to the chosen piece set directory (e.g. the folder
                that contains the per-code piece directories). Switching
                between piece sets is done by changing this path.

            board_path:
                Path to the board background image.

            cell_size:
                Target size in pixels for a single piece frame.

            image_factory:
                Callable that creates a new, empty ``Img`` instance.
                Defaults to the provided ``Img`` class and is injectable
                so tests can supply a lightweight double.

            sprite_extension:
                File extension used for sprite frame files.
        """
        self._pieces_root = Path(pieces_root)
        self._board_path = Path(board_path)
        self._cell_size = cell_size
        self._image_factory = image_factory
        self._sprite_extension = sprite_extension
        self._cache: dict[tuple[str, str], AnimationData] = {}

    def get_animation(self, code: str, state: str) -> AnimationData:
        """
        Returns the cached animation data for a piece code and state.
        """
        key = (code, state)

        if key not in self._cache:
            self._cache[key] = self._load_animation(code, state)

        return self._cache[key]

    def background(self) -> Img:
        """
        Returns a fresh board background image to be used as a render
        canvas. Loaded at its original size and not cached, since drawing
        onto it mutates the image.
        """
        return self._read(self._board_path, None)

    def _load_animation(self, code: str, state: str) -> AnimationData:
        state_dir = self._pieces_root / code / STATES_DIRNAME / state

        config = self._load_config(state_dir / CONFIG_FILENAME)
        frames = self._load_frames(state_dir / SPRITES_DIRNAME)

        physics = config[CONFIG_PHYSICS]
        graphics = config[CONFIG_GRAPHICS]

        return AnimationData(
            frames=frames,
            fps=graphics[CONFIG_FPS],
            is_loop=graphics[CONFIG_IS_LOOP],
            next_state_when_finished=physics[CONFIG_NEXT_STATE],
            speed_m_per_sec=physics[CONFIG_SPEED],
        )

    def _load_config(self, path: Path) -> dict:
        with open(path, encoding="utf-8") as config_file:
            return json.load(config_file)

    def _load_frames(self, sprites_dir: Path) -> tuple[Img, ...]:
        paths = sorted(
            sprites_dir.glob(f"*{self._sprite_extension}"),
            key=lambda path: int(path.stem),
        )

        return tuple(
            self._read(path, (self._cell_size, self._cell_size))
            for path in paths
        )

    def _read(self, path: Path, size: tuple[int, int] | None) -> Img:
        image = self._image_factory()

        if size is None:
            image.read(str(path))
        else:
            image.read(str(path), size=size, keep_aspect=True)

        return image
