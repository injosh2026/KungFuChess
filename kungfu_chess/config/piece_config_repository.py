from pathlib import Path
import json

from kungfu_chess.config.config_error import InvalidConfigError
from kungfu_chess.config.state_config import (GraphicsConfig, PhysicsConfig, StateConfig)


class PieceConfigRepository:
    def __init__(self, assets_root: Path):
        self._assets_root = assets_root
        self._cache: dict[tuple[str, str], StateConfig] = {}

    def _config_path(self, piece_code: str, state_name: str) -> Path:
        return (
            self._assets_root
        / "pieces2"
        / piece_code
        / "states"
        / state_name
        / "config.json"
    )

    def load_state(self, piece_code: str, state_name: str) -> StateConfig:
        cache_key = (piece_code, state_name)

        if cache_key in self._cache:
            return self._cache[cache_key]

        config_path = self._config_path(piece_code, state_name)
            
        with config_path.open(encoding="utf-8") as file:
            data = json.load(file)

        self._validate_state_config(
            piece_code,
            state_name,
            data,
        )

        physics = PhysicsConfig(
            speed_m_per_sec=data["physics"]["speed_m_per_sec"],
            next_state_when_finished=data["physics"]["next_state_when_finished"],
            # duration_ms=data["physics"]["duration_ms"],
        )

        graphics = GraphicsConfig(
            frames_per_sec=data["graphics"]["frames_per_sec"],
            is_loop=data["graphics"]["is_loop"],
        )

        state_config = StateConfig(
            physics=physics,
            graphics=graphics,
        )

        self._cache[cache_key] = state_config

        return state_config
    
    def state_exists(self, piece_code: str, state_name: str) -> bool:
        return self._config_path(
            piece_code,
            state_name
        ).exists()
    
    def _validate_state_config(self, piece_code: str, state_name: str, data: dict) -> None:
        if "physics" not in data:
            raise InvalidConfigError(
                f"Missing physics section in {piece_code}/{state_name}"
            )

        if "graphics" not in data:
            raise InvalidConfigError(
                f"Missing graphics section in {piece_code}/{state_name}"
            )

        physics = data["physics"]

        if "speed_m_per_sec" not in physics:
            raise InvalidConfigError(
                f"Missing speed_m_per_sec in {piece_code}/{state_name}"
            )

        if "next_state_when_finished" not in physics:
            raise InvalidConfigError(
                f"Missing next_state_when_finished in {piece_code}/{state_name}"
            )

        next_state = physics["next_state_when_finished"]

        if not self.state_exists(piece_code, next_state):
            raise InvalidConfigError(
                f"Unknown next state '{next_state}' "
                f"for {piece_code}/{state_name}"
            )