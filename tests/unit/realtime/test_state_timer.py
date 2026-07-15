from kungfu_chess.realtime.state_timer import StateTimer

PIECE_ID = 1
DURATION_MS = 1000


def test_progress_is_zero_when_timer_starts():
    timer = StateTimer()
    timer.start(PIECE_ID, DURATION_MS)

    assert timer.progress(PIECE_ID) == 0.0


def test_progress_increases_with_time():
    timer = StateTimer()
    timer.start(PIECE_ID, DURATION_MS)

    timer.advance(250)

    assert timer.progress(PIECE_ID) == 0.25


def test_progress_reaches_one_when_timer_finishes():
    timer = StateTimer()
    timer.start(PIECE_ID, DURATION_MS)

    finished = timer.advance(DURATION_MS)

    assert finished == [PIECE_ID]
    assert timer.progress(PIECE_ID) is None


def test_advance_returns_finished_piece_ids():
    timer = StateTimer()
    timer.start(PIECE_ID, DURATION_MS)

    assert timer.advance(999) == []
    assert timer.advance(1) == [PIECE_ID]


def test_start_replaces_existing_timer():
    timer = StateTimer()
    timer.start(PIECE_ID, DURATION_MS)
    timer.advance(500)

    timer.start(PIECE_ID, DURATION_MS)

    assert timer.progress(PIECE_ID) == 0.0


def test_advance_can_skip_newly_started_timers():
    timer = StateTimer()
    timer.start(1, DURATION_MS)

    assert timer.advance(500, only_piece_ids=frozenset()) == []
    assert timer.progress(1) == 0.0


def test_active_piece_ids_returns_running_timers():
    timer = StateTimer()

    assert timer.active_piece_ids() == []

    timer.start(PIECE_ID, DURATION_MS)

    assert timer.active_piece_ids() == [PIECE_ID]


def test_progress_is_none_for_unknown_piece():
    timer = StateTimer()

    assert timer.progress(PIECE_ID) is None


def test_has_active_timer_is_false_for_unknown_piece():
    timer = StateTimer()

    assert timer.has_active_timer(PIECE_ID) is False


def test_has_active_timer_is_true_while_timer_runs():
    timer = StateTimer()
    timer.start(PIECE_ID, DURATION_MS)

    assert timer.has_active_timer(PIECE_ID) is True


def test_has_active_timer_is_false_after_timer_finishes():
    timer = StateTimer()
    timer.start(PIECE_ID, DURATION_MS)
    timer.advance(DURATION_MS)

    assert timer.has_active_timer(PIECE_ID) is False
