from enum import Enum, auto


class RuntimeRole(Enum):
    """
    Semantic runtime timing roles exposed on piece snapshots.

    These describe kinds of timed runtime processes, not engine trackers
    or presentation decisions.
    """

    ACTIVE_ABILITY = auto()
    RECOVERY = auto()
