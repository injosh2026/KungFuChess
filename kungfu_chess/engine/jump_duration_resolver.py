import math

from kungfu_chess.config.config_error import InvalidConfigError
from kungfu_chess.config.piece_config_repository import PieceConfigRepository

MS_PER_SECOND = 1000


class JumpDurationResolver:
    """
    Derives jump action duration from jump animation settings.

    Duration is based on sprite frame count and frames_per_sec from config,
    not on physics.duration_ms.
    """

    def __init__(self, config_repository: PieceConfigRepository):
        self._config_repository = config_repository

    def duration_ms(self, piece_code: str, jump_state_name: str) -> int:
        config = self._config_repository.load_state(piece_code, jump_state_name)
        frame_count = self._config_repository.count_sprite_frames(
            piece_code,
            jump_state_name,
        )
        fps = config.graphics.frames_per_sec

        if fps <= 0:
            raise InvalidConfigError(
                f"frames_per_sec must be positive for {piece_code}/{jump_state_name}"
            )

        if frame_count == 0:
            raise InvalidConfigError(
                f"No sprite frames found for {piece_code}/{jump_state_name}"
            )

        return math.ceil(frame_count * MS_PER_SECOND / fps)
