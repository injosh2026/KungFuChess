from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter


def create_motion():
    return Motion(
        piece_id=1, start=Position(0, 0), target=Position(0, 5), duration_ms=1000
    )


def test_arbiter_starts_motion_when_empty():

    arbiter = RealTimeArbiter()
    motion = create_motion()

    result = arbiter.start_motion(motion)

    assert result is True
    assert arbiter.has_active_motion() is True
    assert arbiter.active_motion == motion


def test_arbiter_rejects_second_motion():

    arbiter = RealTimeArbiter()

    first = create_motion()
    second = create_motion()

    arbiter.start_motion(first)

    result = arbiter.start_motion(second)

    assert result is False
    assert arbiter.active_motion == first


def test_advance_time_updates_active_motion():

    arbiter = RealTimeArbiter()
    motion = create_motion()

    arbiter.start_motion(motion)

    arbiter.advance_time(500)

    assert motion.elapsed_ms == 500


def test_completed_motion_is_removed():

    arbiter = RealTimeArbiter()
    motion = create_motion()

    arbiter.start_motion(motion)

    arbiter.advance_time(1000)

    assert arbiter.has_active_motion() is False
    assert arbiter.active_motion is None


def test_advance_time_without_motion_does_nothing():

    arbiter = RealTimeArbiter()

    arbiter.advance_time(500)

    assert arbiter.has_active_motion() is False
