from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter


def create_motion(piece_id=1, start_row=0, start_col=0, target_col=5):
    return Motion(
        piece_id=piece_id,
        start=Position(start_row, start_col),
        target=Position(start_row, target_col),
        duration_ms=1000,
    )


def test_arbiter_starts_motion_when_empty():

    arbiter = RealTimeArbiter()
    motion = create_motion()

    result = arbiter.start_motion(motion)

    assert result is True
    assert arbiter.has_any_motion() is True
    assert arbiter.has_motion(1) is True
    assert arbiter.get_motion(1) == motion
    assert arbiter.active_motions() == (motion,)


def test_arbiter_rejects_second_motion_for_same_piece():

    arbiter = RealTimeArbiter()

    first = create_motion()
    second = create_motion()

    arbiter.start_motion(first)

    result = arbiter.start_motion(second)

    assert result is False
    assert arbiter.get_motion(1) == first
    assert arbiter.active_motions() == (first,)


def test_arbiter_allows_parallel_motions_for_different_pieces():

    arbiter = RealTimeArbiter()

    first = create_motion(piece_id=1)
    second = create_motion(piece_id=2, start_row=2)

    assert arbiter.start_motion(first) is True
    assert arbiter.start_motion(second) is True

    assert arbiter.active_piece_ids() == frozenset({1, 2})
    assert len(arbiter.active_motions()) == 2
    assert arbiter.get_motion(1) == first
    assert arbiter.get_motion(2) == second


def test_advance_time_updates_all_active_motions():

    arbiter = RealTimeArbiter()
    first = create_motion(piece_id=1)
    second = create_motion(piece_id=2, start_row=2)

    arbiter.start_motion(first)
    arbiter.start_motion(second)

    completed = arbiter.advance_time(500)

    assert completed == []
    assert first.elapsed_ms == 500
    assert second.elapsed_ms == 500


def test_completed_motion_is_removed():

    arbiter = RealTimeArbiter()
    motion = create_motion()

    arbiter.start_motion(motion)

    completed = arbiter.advance_time(1000)

    assert completed == [motion]
    assert arbiter.has_any_motion() is False
    assert arbiter.get_motion(1) is None


def test_two_motions_complete_in_same_tick():

    arbiter = RealTimeArbiter()
    first = create_motion(piece_id=1)
    second = create_motion(piece_id=2, start_row=2)

    arbiter.start_motion(first)
    arbiter.start_motion(second)

    completed = arbiter.advance_time(1000)

    assert completed == [first, second]
    assert arbiter.has_any_motion() is False


def test_advance_time_without_motion_does_nothing():

    arbiter = RealTimeArbiter()

    completed = arbiter.advance_time(500)

    assert completed == []
    assert arbiter.has_any_motion() is False


def test_cancel_motion_removes_existing_motion():
    arbiter = RealTimeArbiter()
    motion = create_motion()

    arbiter.start_motion(motion)

    removed = arbiter.cancel_motion(1)

    assert removed == motion
    assert arbiter.has_motion(1) is False
    assert arbiter.active_motions() == ()


def test_cancel_motion_returns_none_for_unknown_piece_id():
    arbiter = RealTimeArbiter()

    removed = arbiter.cancel_motion(99)

    assert removed is None


def test_cancelled_motion_is_not_completed_by_advance_time():
    arbiter = RealTimeArbiter()
    motion = create_motion()

    arbiter.start_motion(motion)
    arbiter.cancel_motion(1)

    completed = arbiter.advance_time(1000)

    assert completed == []
    assert arbiter.has_any_motion() is False


def test_start_motion_works_after_cancel():
    arbiter = RealTimeArbiter()
    first = create_motion()
    second = create_motion(target_col=4)

    arbiter.start_motion(first)
    arbiter.cancel_motion(1)

    result = arbiter.start_motion(second)

    assert result is True
    assert arbiter.get_motion(1) == second
