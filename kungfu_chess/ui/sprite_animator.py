from img import Img
from kungfu_chess.ui.animation_data import AnimationData

MS_PER_SECOND = 1000


class SpriteAnimator:
    """
    Selects the current animation frame from AnimationData.

    SpriteAnimator manages only the progression of a single animation:
    given an elapsed time it returns the frame that should be shown. It
    contains no game rules and does not decide state transitions.
    """

    def __init__(self, animation: AnimationData):
        self._animation = animation

    def frame_at(self, elapsed_ms: int) -> Img:
        """
        Returns the frame that should be shown after ``elapsed_ms``.

        Raises:
            ValueError: if the animation has no frames.
        """
        frames = self._animation.frames

        if not frames:
            raise ValueError("Animation has no frames")

        return frames[self._frame_index(elapsed_ms, len(frames))]

    def _frame_index(self, elapsed_ms: int, frame_count: int) -> int:
        if frame_count <= 1 or self._animation.fps <= 0:
            return 0

        frame_duration_ms = MS_PER_SECOND / self._animation.fps
        index = int(elapsed_ms // frame_duration_ms)

        if self._animation.is_loop:
            return index % frame_count

        return min(index, frame_count - 1)

    def frame_at_progress(self, progress: float) -> Img:
        frames = self._animation.frames

        if not frames:
            raise ValueError("Animation has no frames")

        frame_count = len(frames)
        if frame_count <= 1:
            return frames[0]

        index = min(int(progress * frame_count), frame_count - 1)
        return frames[index]
