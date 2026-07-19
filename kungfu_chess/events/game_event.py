from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GameEvent:
    """
    Base type for chronological game events published by the engine.

    Subclasses carry domain data only. They must not contain UI formatting
    or presentation decisions.
    """

    timestamp_ms: int
