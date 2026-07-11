from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion


def create_motion():
    return Motion(
        piece_id=1, start=Position(0, 0), target=Position(0, 5), duration_ms=1000
    )


def test_motion_starts_with_zero_elapsed_time():

    motion = create_motion()

    assert motion.elapsed_ms == 0
    assert motion.is_completed is False


def test_motion_advances_time():

    motion = create_motion()

    motion.advance_time(500)

    assert motion.elapsed_ms == 500
    assert motion.is_completed is False


def test_motion_completes_after_duration():

    motion = create_motion()

    motion.advance_time(1000)

    assert motion.is_completed is True


def test_motion_can_complete_after_passing_duration():

    motion = create_motion()

    motion.advance_time(1500)

    assert motion.is_completed is True
