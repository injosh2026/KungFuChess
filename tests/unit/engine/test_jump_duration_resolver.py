from pathlib import Path

from kungfu_chess.config.piece_config_repository import PieceConfigRepository
from kungfu_chess.engine.jump_duration_resolver import JumpDurationResolver

ASSETS_ROOT = Path(__file__).resolve().parents[3] / "assets"


def test_jump_duration_from_sprite_count_and_fps():
    repository = PieceConfigRepository(ASSETS_ROOT)
    resolver = JumpDurationResolver(repository)

    duration_ms = resolver.duration_ms("NW", "jump")

    assert duration_ms == 1000
