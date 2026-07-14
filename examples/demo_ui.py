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

from pathlib import Path

from img import Img
from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.io.board_parser import BoardParser
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.ui.animation_clock import AnimationClock
from kungfu_chess.ui.animation_provider import AnimationProvider
from kungfu_chess.ui.graphical_renderer import GraphicalRenderer
from kungfu_chess.ui.sprite_library import SpriteLibrary
from kungfu_chess.view.snapshot_builder import SnapshotBuilder

ASSETS_ROOT = Path(__file__).resolve().parents[1] / "assets"
PIECE_SET = "pieces2"
BOARD_FILENAME = "board.png"
CELL_SIZE = 100
PRESENT_WAIT_MS = 50

ASSET_STATE_BY_PIECE_STATE = {
    PieceState.IDLE: "idle",
    PieceState.MOVING: "move",
}

STARTING_BOARD = [
    "bR bN bB bQ bK bB bN bR",
    "bP bP bP bP bP bP bP bP",
    ".  .  .  .  .  .  .  .",
    ".  .  .  .  .  .  .  .",
    ".  .  .  .  .  .  .  .",
    ".  .  .  .  .  .  .  .",
    "wP wP wP wP wP wP wP wP",
    "wR wN wB wQ wK wB wN wR",
]


def build_snapshot():
    board = BoardParser().parse(STARTING_BOARD)
    _, game_engine = GameFactory.create(board)
    return SnapshotBuilder().build(game_engine.game_state)


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
