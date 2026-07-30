from collections.abc import Iterable

from kungfu_chess.realtime.motion import Motion


def index_motions_by_piece_id(
    motions: Iterable[Motion] | None,
) -> dict[int, Motion]:
    motion_by_piece_id: dict[int, Motion] = {}

    if motions:
        for motion in motions:
            motion_by_piece_id[motion.piece_id] = motion

    return motion_by_piece_id


def visual_position_for_motion(
    motion: Motion,
    visual_position_calculator,
) -> tuple[float, float]:
    progress = min(motion.elapsed_ms / motion.duration_ms, 1.0)
    return visual_position_calculator.calculate(
        motion.start,
        motion.target,
        progress,
    )


def visual_position_for_piece(
    piece_id: int,
    motion_by_piece_id: dict[int, Motion],
    visual_position_calculator,
) -> tuple[float, float] | None:
    motion = motion_by_piece_id.get(piece_id)
    if motion is None:
        return None

    return visual_position_for_motion(motion, visual_position_calculator)
