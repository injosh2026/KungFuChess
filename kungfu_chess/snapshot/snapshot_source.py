from abc import ABC, abstractmethod

from kungfu_chess.snapshot.game_snapshot import GameSnapshot


class SnapshotSource(ABC):
    """
    Provides the current game snapshot.

    Implementations may obtain snapshots from
    local game state or remote network sources.
    """

    @abstractmethod
    def get_snapshot(self) -> GameSnapshot:
        pass