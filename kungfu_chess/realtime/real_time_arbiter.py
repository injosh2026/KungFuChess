from kungfu_chess.realtime.motion import Motion


class RealTimeArbiter:
    """
    Manages the time progression of active piece movements.

    RealTimeArbiter tracks motions currently in progress,
    advances their elapsed time, and returns motions that
    have completed. At most one motion may be active per piece.

    It does not validate moves, modify the board,
    or resolve collisions.
    """

    def __init__(self):
        """
        Creates an empty movement tracker.
        """
        self._active_motions: dict[int, Motion] = {}

    def has_any_motion(self) -> bool:
        """
        Checks whether there are any active movements.

        Returns:
            True if at least one motion is currently active.
        """
        return len(self._active_motions) > 0

    def has_motion(self, piece_id: int) -> bool:
        """
        Checks whether a specific piece has an active movement.

        Returns:
            True if the piece is currently moving.
        """
        return piece_id in self._active_motions

    def get_motion(self, piece_id: int) -> Motion | None:
        """
        Returns the active motion for a piece, if any.

        Returns:
            The active motion for the piece, or None.
        """
        return self._active_motions.get(piece_id)

    def active_motions(self) -> tuple[Motion, ...]:
        """
        Returns all currently active motions.

        Returns:
            Immutable snapshot of active motions.
        """
        return tuple(self._active_motions.values())

    def active_piece_ids(self) -> frozenset[int]:
        """
        Returns the ids of all pieces with an active motion.

        Returns:
            Frozen set of piece ids.
        """
        return frozenset(self._active_motions.keys())

    def start_motion(self, motion: Motion) -> bool:
        """
        Starts tracking a new motion.

        Args:
            motion:
                Movement to track.

        Returns:
            True if the motion was added,
            False if this piece already has an active motion.
        """
        if self.has_motion(motion.piece_id):
            return False

        self._active_motions[motion.piece_id] = motion
        return True

    def cancel_motion(self, piece_id: int) -> Motion | None:
        """
        Removes an active motion for a piece.

        Args:
            piece_id:
                Identifier of the piece whose motion should be cancelled.

        Returns:
            The removed motion if one was active, otherwise None.
        """
        return self._active_motions.pop(piece_id, None)

    def advance_time(self, milliseconds: int) -> list[Motion]:
        """
        Advances game time for all active motions.

        Args:
            milliseconds:
                Amount of time to advance.

        Returns:
            List of motions that completed during this update.
        """
        completed_motions = []

        for motion in self._active_motions.values():
            motion.advance_time(milliseconds)

            if motion.is_completed:
                completed_motions.append(motion)

        for motion in completed_motions:
            del self._active_motions[motion.piece_id]

        return completed_motions
