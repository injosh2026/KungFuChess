from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MoveHistoryEntry:
    """
    Immutable presentation record for one completed move.

    Intended for side panels, replay, and future spectator views.
    """

    elapsed_time_ms: int
    piece_code: str
    piece_name: str
    from_square: str
    to_square: str
    was_capture: bool = False
    promotion: str | None = None
    jump: bool = False
