from kungfu_chess.ui.animation_data import AnimationData


def test_stores_animation_metadata():
    animation = AnimationData(
        frames=(),
        fps=6,
        is_loop=True,
        next_state_when_finished="idle",
        speed_m_per_sec=0.0,
    )

    assert animation.fps == 6
    assert animation.is_loop is True
    assert animation.next_state_when_finished == "idle"
    assert animation.speed_m_per_sec == 0.0
