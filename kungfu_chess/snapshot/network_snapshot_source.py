from dataclasses import replace

from kungfu_chess.snapshot.game_snapshot import GameSnapshot
from kungfu_chess.snapshot.snapshot_source import SnapshotSource


class NetworkSnapshotSource(SnapshotSource):
    """
    Provides snapshots received from a remote server.

    The source does not know about networking details.
    It only consumes already received snapshots.

    When a controller is provided, local selection state is overlaid
    onto the latest server snapshot for rendering.
    """

    def __init__(self, connection, controller=None):
        self._connection = connection
        self._controller = controller
        self._latest_snapshot = None

    def update(self, snapshot: GameSnapshot) -> None:
        self._latest_snapshot = snapshot

    def get_snapshot(self) -> GameSnapshot | None:
        if self._latest_snapshot is None:
            return None

        if self._controller is None:
            return self._latest_snapshot

        return replace(
            self._latest_snapshot,
            selected_cell=self._controller.selected_position,
            legal_moves=set(self._controller.legal_moves),
        )
