import json
from pathlib import Path

import pytest

from kungfu_chess.config.config_error import InvalidConfigError
from kungfu_chess.config.piece_config_repository import PieceConfigRepository


def create_state_config(
    root: Path,
    piece_code: str,
    state_name: str,
    next_state: str,
):
    state_dir = (
        root
        / "pieces2"
        / piece_code
        / "states"
        / state_name
    )

    state_dir.mkdir(parents=True)

    config = {
        "physics": {
            "speed_m_per_sec": 1.5,
            "next_state_when_finished": next_state,
        },
        "graphics": {
            "frames_per_sec": 12,
            "is_loop": True,
        },
    }

    with (state_dir / "config.json").open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(config, file)
        

def test_load_move_state():
    repository = PieceConfigRepository(Path("assets"))

    config = repository.load_state("QW", "move")

    assert config.physics.speed_m_per_sec == 1.5
    assert config.physics.next_state_when_finished == "long_rest"

    assert config.graphics.frames_per_sec == 12
    assert config.graphics.is_loop is True


def test_get_move_command_state_from_defaults():
    repository = PieceConfigRepository(Path("assets"))

    assert repository.get_move_command_state("QW") == "move"


def test_get_jump_command_state_from_defaults():
    repository = PieceConfigRepository(Path("assets"))

    assert repository.get_jump_command_state("QW") == "jump"


def test_load_state_returns_cached_instance():
    repository = PieceConfigRepository(Path("assets"))

    first = repository.load_state("QW", "move")
    second = repository.load_state("QW", "move")

    assert first is second


def test_state_exists():
    repository = PieceConfigRepository(Path("assets"))

    assert repository.state_exists("QW", "move") is True


def test_missing_state_does_not_exist():
    repository = PieceConfigRepository(Path("assets"))

    assert repository.state_exists("QW", "does_not_exist") is False

def test_missing_next_state_raises_error(tmp_path):
    create_state_config(
        tmp_path,
        "QW",
        "move",
        "does_not_exist",
    )

    repository = PieceConfigRepository(tmp_path)

    with pytest.raises(InvalidConfigError):
        repository.load_state("QW", "move")


def test_missing_physics_section_raises_error(tmp_path):
    state_dir = (
        tmp_path
        / "pieces2"
        / "QW"
        / "states"
        / "move"
    )

    state_dir.mkdir(parents=True)

    config = {
        "graphics": {
            "frames_per_sec": 12,
            "is_loop": True,
        }
    }

    with (state_dir / "config.json").open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(config, file)

    repository = PieceConfigRepository(tmp_path)

    with pytest.raises(InvalidConfigError):
        repository.load_state("QW", "move")


def test_missing_speed_raises_error(tmp_path):
    create_state_config(
        tmp_path,
        "QW",
        "move",
        "idle",
    )

    config_path = (
        tmp_path
        / "pieces2"
        / "QW"
        / "states"
        / "move"
        / "config.json"
    )

    with config_path.open(
        encoding="utf-8"
    ) as file:
        config = json.load(file)

    del config["physics"]["speed_m_per_sec"]

    with config_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(config, file)

    repository = PieceConfigRepository(tmp_path)

    with pytest.raises(InvalidConfigError):
        repository.load_state("QW", "move")