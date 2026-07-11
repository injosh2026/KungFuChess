from kungfu_chess.realtime.motion import Motion


class RealTimeArbiter:

    def __init__(self):
        self._active_motion: Motion | None = None

    def has_active_motion(self) -> bool:
        return self._active_motion is not None

    def start_motion(self, motion: Motion) -> bool:
        if self.has_active_motion():
            return False

        self._active_motion = motion
        return True

    def advance_time(self, milliseconds: int) -> None:
        if self._active_motion is None:
            return

        self._active_motion.advance_time(milliseconds)

        if self._active_motion.is_completed:
            self._active_motion = None

    @property
    def active_motion(self) -> Motion | None:
        return self._active_motion
