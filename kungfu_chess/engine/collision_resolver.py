from kungfu_chess.engine.collision_decisions import ArrivalOutcome, CaptureAtArrival
from kungfu_chess.model.board import Board
from kungfu_chess.realtime.motion import Motion


class CollisionResolver:
    """
    Applies Kung Fu Chess arrival collision rules.

    CollisionResolver is stateless. It inspects the board and returns
    decisions only. It never mutates game state.
    """

    def sort_arrivals(self, completed: list[Motion]) -> tuple[Motion, ...]:
        """
        Orders completed motions for sequential arrival processing.

        Earlier entries arrive first. Later entries may capture occupants
        placed by earlier arrivals at the same cell.

        Sort key:
            1. motion.duration_ms (relative completion time)
            2. motion.piece_id (deterministic tie-break)
        """
        return tuple(
            sorted(
                completed,
                key=lambda motion: (motion.duration_ms, motion.piece_id),
            )
        )

    def resolve_arrival(self, motion: Motion, board: Board) -> ArrivalOutcome:
        """
        Inspects the target cell before an arrival is applied.

        Args:
            motion:
                Completed motion about to be resolved.
            board:
                Current logical board state.

        Returns:
            ArrivalOutcome describing whether an enemy capture will occur.
        """
        occupant = board.get_piece_by_position(motion.target)

        if occupant is None:
            return ArrivalOutcome()

        mover = board.get_piece_by_id(motion.piece_id)

        if mover is None or occupant.color == mover.color:
            return ArrivalOutcome()

        return ArrivalOutcome(
            capture=CaptureAtArrival(
                capturer_piece_id=motion.piece_id,
                victim_piece_id=occupant.id,
                at_cell=motion.target,
            )
        )
