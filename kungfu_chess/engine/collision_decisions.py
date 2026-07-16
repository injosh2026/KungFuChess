from dataclasses import dataclass

from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion


@dataclass(frozen=True, slots=True)
class CaptureAtArrival:
    """
    Describes an enemy capture when a piece arrives at a cell.

    Used by CollisionResolver for arrival-time analysis only.
    Board mutation is performed by ArrivalResolver.
    """

    capturer_piece_id: int
    victim_piece_id: int
    at_cell: Position


@dataclass(frozen=True, slots=True)
class ArrivalOutcome:
    """
    Result of analyzing a completed motion against the current board.

    When capture is set, the arriving piece is expected to capture the
    occupant at the target cell or on the resolved bounce path.

    When arrival_cell is set, the mover lands on that cell instead of
    motion.target. None means a normal arrival at motion.target.
    """

    capture: CaptureAtArrival | None = None
    arrival_cell: Position | None = None


@dataclass(frozen=True, slots=True)
class EntryOutcome:
    """
    Result of analyzing a mid-path cell entry against current occupancy.

    Board mutation is performed by GameEngine.
    """

    capture: CaptureAtArrival | None = None


@dataclass(frozen=True, slots=True)
class CellOccupant:
    """
    Logical occupant of a cell for collision analysis.

    entry_time_ms is the absolute kinematic time from the motion start.
    """

    piece_id: int
    color: Color
    entry_time_ms: int


@dataclass(frozen=True, slots=True)
class CellEntryEvent:
    piece_id: int
    cell: Position
    time_from_wait_start_ms: int
    motion: Motion
    path_index: int


@dataclass(frozen=True, slots=True)
class MotionCompletionEvent:
    piece_id: int
    motion: Motion
    time_from_wait_start_ms: int


STATIONARY_ENTRY_TIME_MS = 0
ENTRY_EVENT_PRIORITY = 0
COMPLETION_EVENT_PRIORITY = 1
