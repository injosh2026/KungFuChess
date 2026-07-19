from pathlib import Path
from typing import Callable

from img import Img
from kungfu_chess.ui.animation_data import AnimationData
from kungfu_chess.config.piece_config_repository import PieceConfigRepository

STATES_DIRNAME = "states"
SPRITES_DIRNAME = "sprites"
SPRITE_EXTENSION = ".png"

BOARD_CELLS_PER_SIDE = 8
BACKGROUND_COLOR = (60, 60, 60, 255)


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
        config_repository: PieceConfigRepository | None = None,
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
        self._config_repository = config_repository
        self._board_path = Path(board_path)
        self._cell_size = cell_size
        self._image_factory = image_factory
        self._sprite_extension = sprite_extension
        self._cache: dict[tuple[str, str], AnimationData] = {}

        if config_repository is None:
            config_repository = PieceConfigRepository(self._pieces_root.parent)

        self._config_repository = config_repository

    def set_display_cell_size(self, cell_size: int) -> None:
        if cell_size == self._cell_size:
            return

        self._cell_size = cell_size
        self._cache.clear()

    def get_animation(self, code: str, state: str) -> AnimationData:
        """
        Returns the cached animation data for a piece code and state.
        """
        key = (code, state)

        if key not in self._cache:
            self._cache[key] = self._load_animation(code, state)

        return self._cache[key]

    def background(
        self,
        canvas_width: int,
        canvas_height: int,
        board_origin: tuple[int, int],
    ) -> Img:
        """
        Returns a fresh full-canvas background for the current frame.

        The chess board image is resized to the current cell grid and
        drawn at ``board_origin`` on a blank canvas sized to the current
        window.
        """
        canvas = self._image_factory().create_blank(
            canvas_width,
            canvas_height,
            BACKGROUND_COLOR,
        )

        board_side = self._cell_size * BOARD_CELLS_PER_SIDE
        board = self._image_factory()
        board.read(str(self._board_path), size=(board_side, board_side))

        board.draw_on(canvas, board_origin[0], board_origin[1])
        return canvas

    def background_at_original_size(self) -> Img:
        """Returns the board image alone at its original size (for tests)."""
        return self._read(self._board_path, None)

    def _load_animation(self, code: str, state: str) -> AnimationData:
        state_dir = self._pieces_root / code / STATES_DIRNAME / state

        state_config = self._config_repository.load_state(
            code,
            state,
        )

        frames = self._load_frames(state_dir / SPRITES_DIRNAME)

        return AnimationData(
            frames=frames,
            fps=state_config.graphics.frames_per_sec,
            is_loop=state_config.graphics.is_loop,
            next_state_when_finished=(state_config.physics.next_state_when_finished),
            speed_m_per_sec=(state_config.physics.speed_m_per_sec),
        )

    def _load_frames(self, sprites_dir: Path) -> tuple[Img, ...]:
        paths = sorted(
            sprites_dir.glob(f"*{self._sprite_extension}"),
            key=lambda path: int(path.stem),
        )

        return tuple(
            self._read(path, (self._cell_size, self._cell_size)) for path in paths
        )

    def _read(self, path: Path, size: tuple[int, int] | None) -> Img:
        image = self._image_factory()

        if size is None:
            image.read(str(path))
        else:
            image.read(str(path), size=size, keep_aspect=True)

        return image
