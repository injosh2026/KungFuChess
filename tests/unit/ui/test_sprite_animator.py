import pytest

from kungfu_chess.ui.animation_data import AnimationData
from kungfu_chess.ui.sprite_animator import SpriteAnimator


def make_animation(frame_count, fps=10, is_loop=True):
    frames = tuple(f"frame-{i}" for i in range(frame_count))
    return AnimationData(
        frames=frames,
        fps=fps,
        is_loop=is_loop,
        next_state_when_finished="idle",
        speed_m_per_sec=0.0,
    )


def test_first_frame_at_time_zero():
    animator = SpriteAnimator(make_animation(3, fps=10))

    assert animator.frame_at(0) == "frame-0"


def test_advances_frame_by_fps():
    animator = SpriteAnimator(make_animation(3, fps=10))

    # 10 fps -> 100 ms per frame
    assert animator.frame_at(100) == "frame-1"
    assert animator.frame_at(250) == "frame-2"


def test_looping_wraps_around():
    animator = SpriteAnimator(make_animation(3, fps=10, is_loop=True))

    assert animator.frame_at(300) == "frame-0"
    assert animator.frame_at(400) == "frame-1"


def test_non_looping_clamps_to_last_frame():
    animator = SpriteAnimator(make_animation(3, fps=10, is_loop=False))

    assert animator.frame_at(1000) == "frame-2"


def test_single_frame_animation_always_returns_it():
    animator = SpriteAnimator(make_animation(1, fps=10))

    assert animator.frame_at(5000) == "frame-0"


def test_zero_fps_returns_first_frame():
    animator = SpriteAnimator(make_animation(3, fps=0))

    assert animator.frame_at(1000) == "frame-0"


def test_empty_frames_raises_value_error():
    animator = SpriteAnimator(make_animation(0, fps=10))

    with pytest.raises(ValueError):
        animator.frame_at(0)
