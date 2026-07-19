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
from kungfu_chess.ui.composition_root import (
    CanvasSizedVisualPositionCalculator,
    SPRITE_LIBRARY_BOOTSTRAP_CELL_SIZE,
)
from kungfu_chess.ui.board_coordinates_renderer import BoardCoordinatesRenderer
from kungfu_chess.ui.graphical_renderer import GraphicalRenderer
from kungfu_chess.ui.move_history_panel import MoveHistoryPanel
from kungfu_chess.ui.player_panel import PlayerPanel
from kungfu_chess.ui.player_panel_data import PlayerPanelConfig
from kungfu_chess.ui.promotion_picker_overlay import PromotionPickerOverlay
from kungfu_chess.ui.sprite_library import SpriteLibrary
from kungfu_chess.ui.state_progress_overlay import StateProgressOverlay
from kungfu_chess.view.snapshot_builder import SnapshotBuilder
from kungfu_chess.config.demo_config import (
    ASSETS_ROOT,
    BOARD_FILENAME,
    PIECE_SET,
    PRESENT_WAIT_MS,
    STARTING_BOARD,
)


def build_snapshot(canvas_size_provider):
    board = BoardParser().parse(STARTING_BOARD)
    _, game_engine, move_history_observer, score_observer = GameFactory.create(board)
    calculator = CanvasSizedVisualPositionCalculator(canvas_size_provider)

    return SnapshotBuilder(
        calculator,
        get_runtime_progress=game_engine.runtime_progress,
        get_move_history=move_history_observer.entries,
        get_player_scores=score_observer.scores,
    ).build(game_engine.game_state)


def main() -> None:
    pieces_root = ASSETS_ROOT / PIECE_SET
    board_path = ASSETS_ROOT / BOARD_FILENAME

    window = Img()
    window.open_window()
    window.prime_window()

    canvas_size = window.canvas_size

    library = SpriteLibrary(
        pieces_root,
        board_path,
        SPRITE_LIBRARY_BOOTSTRAP_CELL_SIZE,
    )
    clock = AnimationClock()
    provider = AnimationProvider(library, clock)
    renderer = GraphicalRenderer(
        library,
        canvas_size,
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

    snapshot = build_snapshot(canvas_size)

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
