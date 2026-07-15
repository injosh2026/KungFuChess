from dataclasses import dataclass

from kungfu_chess.model.position import Position


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
    occupant at the target cell.
    """

    capture: CaptureAtArrival | None = None
