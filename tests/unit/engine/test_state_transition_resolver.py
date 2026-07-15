import json
from pathlib import Path

from kungfu_chess.config.piece_config_repository import PieceConfigRepository
from kungfu_chess.engine.state_transition_resolver import StateTransitionResolver


def create_state_config(
    root: Path,
    piece_code: str,
    state_name: str,
    next_state: str,
):
    state_dir = root / "pieces2" / piece_code / "states" / state_name
    state_dir.mkdir(parents=True)

    config = {
        "physics": {
            "speed_m_per_sec": 0.0,
            "next_state_when_finished": next_state,
        },
        "graphics": {
            "frames_per_sec": 6,
            "is_loop": True,
        },
    }

    (state_dir / "config.json").write_text(
        json.dumps(config),
        encoding="utf-8",
    )


def make_resolver(root: Path) -> StateTransitionResolver:
    return StateTransitionResolver(PieceConfigRepository(root))


def test_move_transitions_to_long_rest_from_config():
    resolver = make_resolver(Path("assets"))

    assert resolver.resolve("QW", "move") == "long_rest"


def test_arbitrary_state_name_works_without_hardcode(tmp_path):
    create_state_config(tmp_path, "QW", "idle", "idle")
    create_state_config(tmp_path, "QW", "custom_taunt", "idle")

    resolver = make_resolver(tmp_path)

    assert resolver.resolve("QW", "custom_taunt") == "idle"


def test_same_next_state_returns_current_state(tmp_path):
    create_state_config(tmp_path, "QW", "idle", "idle")

    resolver = make_resolver(tmp_path)

    assert resolver.resolve("QW", "idle") == "idle"
