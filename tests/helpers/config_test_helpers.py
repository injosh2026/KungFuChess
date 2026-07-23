import json
from pathlib import Path

from kungfu_chess.model.position import Position


def write_piece_defaults(root: Path) -> None:
    defaults = {
        "initial_state": "idle",
        "move_command_state": "move",
        "jump_command_state": "jump",
    }
    defaults_path = root / "pieces2" / "piece_defaults.json"
    defaults_path.parent.mkdir(parents=True, exist_ok=True)
    defaults_path.write_text(
        json.dumps(defaults),
        encoding="utf-8",
    )


def write_state_config(
    root: Path,
    piece_code: str,
    state_name: str,
    next_state: str,
    speed: float = 1.5,
    duration_ms: int | None = None,
) -> None:
    state_dir = root / "pieces2" / piece_code / "states" / state_name
    state_dir.mkdir(parents=True)
    physics = {
        "speed_m_per_sec": speed,
        "next_state_when_finished": next_state,
    }
    if duration_ms is not None:
        physics["duration_ms"] = duration_ms
    config = {
        "physics": physics,
        "graphics": {"frames_per_sec": 12, "is_loop": True},
    }
    (state_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")


def square(name: str) -> Position:
    file_index = ord(name[0]) - ord("a")
    rank_index = int(name[1]) - 1
    return Position(rank_index, file_index)

