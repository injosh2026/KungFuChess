"""
Vertical slice demo for the UI display chain.

Builds a real game with the existing backend (BoardParser + GameFactory),
turns its state into an immutable GameSnapshot via the existing
SnapshotBuilder, and renders the full board with GraphicalRenderer + Img.

Layer boundaries are preserved:
- GraphicalRenderer consumes only the snapshot and ready Img frames; it
  never sees time or the backend.
- SpriteLibrary only loads/caches assets and knows nothing about the game.
- Time enters through an AnimationClock injected into the demo-owned
  AnimationProvider, which selects the asset state and the current frame.

It contains no game loop orchestration (no GameApp) and no input handling
(no MouseInput). Assets are bundled under KungFuChess/assets, so the demo
is self-contained. The board is re-rendered on every iteration so idle
animations play according to the fps in each state's config.json.

Run from the KungFuChess directory:

    python -m examples.demo_ui
"""

from img import Img
from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.io.board_parser import BoardParser
from kungfu_chess.ui.animation_clock import AnimationClock
from kungfu_chess.ui.animation_provider import AnimationProvider
from kungfu_chess.ui.graphical_renderer import GraphicalRenderer
from kungfu_chess.ui.sprite_library import SpriteLibrary
from kungfu_chess.view.snapshot_builder import SnapshotBuilder
from kungfu_chess.config.demo_config import (
    ASSET_STATE_BY_PIECE_STATE,
    ASSETS_ROOT,
    CELL_SIZE,
    BOARD_FILENAME,
    PIECE_SET,
    PRESENT_WAIT_MS,
    STARTING_BOARD,
)
from kungfu_chess.view.visual_position import VisualPositionCalculator


def build_snapshot():
    board = BoardParser().parse(STARTING_BOARD)
    _, game_engine = GameFactory.create(board)
    calculator = VisualPositionCalculator(CELL_SIZE)

    return SnapshotBuilder(calculator).build(game_engine.game_state)


def main() -> None:
    pieces_root = ASSETS_ROOT / PIECE_SET
    board_path = ASSETS_ROOT / BOARD_FILENAME

    library = SpriteLibrary(pieces_root, board_path, CELL_SIZE)
    clock = AnimationClock()
    provider = AnimationProvider(library, clock, ASSET_STATE_BY_PIECE_STATE)
    renderer = GraphicalRenderer(library, CELL_SIZE, provider.frame_for)

    snapshot = build_snapshot()

    window = Img()
    window.open_window()
    try:
        while True:
            frame = renderer.render(snapshot)
            frame.present(PRESENT_WAIT_MS)
    except KeyboardInterrupt:
        pass
    finally:
        window.close()


if __name__ == "__main__":
    main()
