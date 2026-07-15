from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PhysicsConfig:
    speed_m_per_sec: float
    next_state_when_finished: str
    duration_ms: int | None = None


@dataclass(frozen=True, slots=True)
class GraphicsConfig:
    frames_per_sec: int
    is_loop: bool


@dataclass(frozen=True, slots=True)
class StateConfig:
    physics: PhysicsConfig
    graphics: GraphicsConfig