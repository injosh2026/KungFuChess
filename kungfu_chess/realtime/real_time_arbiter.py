from kungfu_chess.realtime.motion import Motion


class RealTimeArbiter:

    def __init__(self):
        self._active_motions: list[Motion] = []

    def has_active_motion(self) -> bool:
        return len(self._active_motions) > 0

    def start_motion(self, motion: Motion) -> bool:
        if self.has_active_motion():
            return False

        self._active_motions.append(motion)
        return True

    def advance_time(self, milliseconds: int) -> list[Motion]:
        completed_motions = []

        for motion in self._active_motions:
            motion.advance_time(milliseconds)
        
            if motion.is_completed:
                completed_motions.append(motion)

        self._active_motions = [
            motion
            for motion in self._active_motions
            if not motion.is_completed
        ]
        
        return completed_motions


    @property
    def active_motion(self) -> Motion | None:
        return self._active_motions[0] if self.has_active_motion() else None
