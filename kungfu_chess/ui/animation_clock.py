import time
from typing import Callable

MS_PER_SECOND = 1000


class AnimationClock:
    """
    Minimal real-time source for animation.

    Reports the elapsed milliseconds since the clock was created or last
    reset. The underlying time source is injectable so tests can drive it
    deterministically. It contains no game logic and no rendering.
    """

    def __init__(self, time_source: Callable[[], float] = time.monotonic):
        self._time_source = time_source
        self._start = time_source()

    def reset(self) -> None:
        self._start = self._time_source()

    def elapsed_ms(self) -> int:
        return int((self._time_source() - self._start) * MS_PER_SECOND)
