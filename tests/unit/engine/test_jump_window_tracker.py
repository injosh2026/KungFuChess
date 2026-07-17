from kungfu_chess.engine.jump_window_tracker import JumpWindowTracker


def test_start_marks_window_active():
    tracker = JumpWindowTracker()

    tracker.start(piece_id=1, duration_ms=500)

    assert tracker.is_active_at(1, 0) is True
    assert tracker.is_active_at(1, 499) is True
    assert tracker.is_active_at(1, 500) is False


def test_advance_expires_window():
    tracker = JumpWindowTracker()
    tracker.start(piece_id=1, duration_ms=500)

    finished = tracker.advance(500)

    assert finished == [1]
    assert tracker.is_active_at(1, 0) is False


def test_clear_removes_window():
    tracker = JumpWindowTracker()
    tracker.start(piece_id=1, duration_ms=500)

    tracker.clear(1)

    assert tracker.is_active_at(1, 0) is False
    assert tracker.progress(1) is None


def test_progress_returns_none_without_active_window():
    tracker = JumpWindowTracker()

    assert tracker.progress(1) is None


def test_progress_returns_zero_at_start():
    tracker = JumpWindowTracker()
    tracker.start(piece_id=1, duration_ms=500)

    assert tracker.progress(1) == 0.0


def test_progress_advances_with_elapsed_time():
    tracker = JumpWindowTracker()
    tracker.start(piece_id=1, duration_ms=500)
    tracker.advance(250)

    assert tracker.progress(1) == 0.5


def test_progress_clamps_to_one():
    tracker = JumpWindowTracker()
    tracker.start(piece_id=1, duration_ms=500)
    tracker.advance(500)

    assert tracker.progress(1) is None
