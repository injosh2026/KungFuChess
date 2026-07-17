from dataclasses import dataclass

from img import Img


@dataclass(frozen=True, slots=True)
class AnimationData:
    """
    Immutable animation data for a single piece state.

    Holds the loaded frames together with the values read from the
    state's config.json. It carries data only and does not advance the
    animation or decide state transitions.
    """

    frames: tuple[Img, ...]
    fps: float
    is_loop: bool
    next_state_when_finished: str
    speed_m_per_sec: float
