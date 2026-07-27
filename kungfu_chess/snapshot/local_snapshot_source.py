from kungfu_chess.snapshot.snapshot_source import SnapshotSource
from kungfu_chess.snapshot.game_snapshot import GameSnapshot


class LocalSnapshotSource(SnapshotSource):
    """
    Creates snapshots from the local running game.

    Used for single-player/local multiplayer mode.
    """

    def __init__(
        self,
        snapshot_builder,
        game_engine,
        controller,
    ):
        self._snapshot_builder = snapshot_builder
        self._game_engine = game_engine
        self._controller = controller


    def get_snapshot(self) -> GameSnapshot:

        return self._snapshot_builder.build(
            self._game_engine.game_state,
            self._controller.selected_position,
            self._game_engine.active_motions(),
            self._controller.legal_moves,
        )