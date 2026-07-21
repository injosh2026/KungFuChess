from kungfu_chess.events.move_performed_event import MovePerformedEvent
from kungfu_chess.history.move_history_observer import MoveHistoryObserver
from kungfu_chess.model.position import Position


def test_observer_records_move_performed_event():
    observer = MoveHistoryObserver()

    observer.handle(
        MovePerformedEvent(
            timestamp_ms=83000,
            piece_id=1,
            piece_code="PW",
            piece_name="pawn",
            from_position=Position(6, 4),
            to_position=Position(4, 4),
        )
    )

    entries = observer.entries()
    assert len(entries) == 1
    assert entries[0].elapsed_time_ms == 83000
    assert entries[0].piece_name == "pawn"
    assert entries[0].from_square == "e2"
    assert entries[0].to_square == "e4"
    assert entries[0].was_capture is False
    assert entries[0].promotion is None
    assert entries[0].jump is False


def test_observer_appends_entries_chronologically():
    observer = MoveHistoryObserver()

    observer.handle(
        MovePerformedEvent(
            timestamp_ms=1000,
            piece_id=1,
            piece_code="RW",
            piece_name="rook",
            from_position=Position(0, 0),
            to_position=Position(0, 1),
        )
    )
    observer.handle(
        MovePerformedEvent(
            timestamp_ms=2000,
            piece_id=2,
            piece_code="RB",
            piece_name="rook",
            from_position=Position(7, 0),
            to_position=Position(7, 1),
            capture="PW",
        )
    )

    entries = observer.entries()
    assert len(entries) == 2
    assert entries[0].elapsed_time_ms == 1000
    assert entries[1].elapsed_time_ms == 2000
    assert entries[1].was_capture is True


def test_observer_ignores_unknown_event_types():
    from kungfu_chess.events.game_event import GameEvent

    observer = MoveHistoryObserver()
    observer.handle(GameEvent(timestamp_ms=1))

    assert observer.entries() == ()
