from pathlib import Path
import json

from kungfu_chess.config.config_error import InvalidConfigError
from kungfu_chess.config.piece_manifest import PieceManifest
from kungfu_chess.config.state_config import GraphicsConfig, PhysicsConfig, StateConfig

PIECE_SET_DIRNAME = "pieces2"
PIECE_CONFIG_FILENAME = "piece.json"
PIECE_DEFAULTS_FILENAME = "piece_defaults.json"


class PieceConfigRepository:
    def __init__(self, assets_root: Path):
        self._assets_root = assets_root
        self._cache: dict[tuple[str, str], StateConfig] = {}
        self._piece_manifest_cache: dict[str, PieceManifest] = {}

    def _pieces_root(self) -> Path:
        return self._assets_root / PIECE_SET_DIRNAME

    def _config_path(self, piece_code: str, state_name: str) -> Path:
        return (
            self._pieces_root()
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
            duration_ms=data["physics"].get("duration_ms"),
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

    def get_move_command_state(self, piece_code: str) -> str:
        return self._load_piece_manifest(piece_code).move_command_state

    def get_jump_command_state(self, piece_code: str) -> str:
        return self._load_piece_manifest(piece_code).jump_command_state

    def _load_piece_manifest(self, piece_code: str) -> PieceManifest:
        if piece_code in self._piece_manifest_cache:
            return self._piece_manifest_cache[piece_code]

        piece_config_path = self._pieces_root() / piece_code / PIECE_CONFIG_FILENAME

        if piece_config_path.exists():
            with piece_config_path.open(encoding="utf-8") as file:
                data = json.load(file)
        else:
            defaults_path = self._pieces_root() / PIECE_DEFAULTS_FILENAME
            with defaults_path.open(encoding="utf-8") as file:
                data = json.load(file)

        self._validate_piece_manifest(piece_code, data)

        manifest = PieceManifest(
            initial_state=data["initial_state"],
            move_command_state=data["move_command_state"],
            jump_command_state=data["jump_command_state"],
        )
        self._piece_manifest_cache[piece_code] = manifest
        return manifest

    def state_exists(self, piece_code: str, state_name: str) -> bool:
        return self._config_path(piece_code, state_name).exists()

    def _validate_state_config(
        self, piece_code: str, state_name: str, data: dict
    ) -> None:
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

        if "duration_ms" in physics:
            if physics["duration_ms"] < 0:
                raise InvalidConfigError("duration_ms cannot be negative")

        if "next_state_when_finished" not in physics:
            raise InvalidConfigError(
                f"Missing next_state_when_finished in {piece_code}/{state_name}"
            )

        next_state = physics["next_state_when_finished"]

        if not self.state_exists(piece_code, next_state):
            raise InvalidConfigError(
                f"Unknown next state '{next_state}' " f"for {piece_code}/{state_name}"
            )

    def _validate_piece_manifest(self, piece_code: str, data: dict) -> None:
        if "initial_state" not in data:
            raise InvalidConfigError(
                f"Missing initial_state in piece manifest for {piece_code}"
            )

        if "move_command_state" not in data:
            raise InvalidConfigError(
                f"Missing move_command_state in piece manifest for {piece_code}"
            )

        if "jump_command_state" not in data:
            raise InvalidConfigError(
                f"Missing jump_command_state in piece manifest for {piece_code}"
            )

        for state_name in (
            data["initial_state"],
            data["move_command_state"],
            data["jump_command_state"],
        ):
            if not self.state_exists(piece_code, state_name):
                raise InvalidConfigError(
                    f"Unknown state '{state_name}' in piece manifest for {piece_code}"
                )
