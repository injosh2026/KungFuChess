from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlayerPanelConfig:
    name: str
    player_id: str


@dataclass(frozen=True, slots=True)
class PlayerPanelData:
    name: str
    score: int
