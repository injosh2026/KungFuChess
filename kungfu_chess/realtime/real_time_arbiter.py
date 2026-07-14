from kungfu_chess.realtime.motion import Motion


class RealTimeArbiter:
    """
    Manages the time progression of active piece movements.

    RealTimeArbiter tracks motions currently in progress,
    advances their elapsed time, and returns motions that
    have completed.

    It does not validate moves, modify the board,
    or resolve collisions.
    """

    def __init__(self):
        """
        Creates an empty movement tracker.
        """
        self._active_motions: list[Motion] = []

    def has_active_motion(self) -> bool:
        """
        Checks whether there are any active movements.

        Returns:
            True if at least one motion is currently active.
        """
        return len(self._active_motions) > 0

    def start_motion(self, motion: Motion) -> bool:
        """
        Starts tracking a new motion.

        Currently only one motion can be active at a time.

        Args:
            motion:
                Movement to track.

        Returns:
            True if the motion was added,
            False if another motion is already active.
        """
        if self.has_active_motion():
            return False

        self._active_motions.append(motion)
        return True

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

        for motion in self._active_motions:
            motion.advance_time(milliseconds)

            if motion.is_completed:
                completed_motions.append(motion)

        self._active_motions = [
            motion for motion in self._active_motions if not motion.is_completed
        ]

        return completed_motions

    @property
    def active_motion(self) -> Motion | None:
        """
        Returns the currently active motion.

        This property exists because the current implementation
        supports a single active motion.

        Future versions may expose all active motions instead.
        """
        return self._active_motions[0] if self.has_active_motion() else None
