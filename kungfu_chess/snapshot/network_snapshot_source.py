from kungfu_chess.snapshot.snapshot_source import SnapshotSource
from kungfu_chess.snapshot.game_snapshot import GameSnapshot


class NetworkSnapshotSource(SnapshotSource):
    """
    Provides snapshots received from a remote server.

    The source does not know about networking details.
    It only consumes already received snapshots.
    """

    def __init__(self, connection):
        self._connection = connection
        self._latest_snapshot = None

    def update(self, snapshot: GameSnapshot) -> None:
        self._latest_snapshot = snapshot

    def get_snapshot(self) -> GameSnapshot:
        return self._latest_snapshot