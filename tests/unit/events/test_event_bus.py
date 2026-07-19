from kungfu_chess.events.event_bus import EventBus
from kungfu_chess.events.game_event import GameEvent
from kungfu_chess.events.move_performed_event import MovePerformedEvent
from kungfu_chess.model.position import Position


class RecordingObserver:
    def __init__(self):
        self.events = []

    def on_game_event(self, event: GameEvent) -> None:
        self.events.append(event)


def make_move_event(timestamp_ms=1000):
    return MovePerformedEvent(
        timestamp_ms=timestamp_ms,
        piece_id=1,
        piece_code="RW",
        piece_name="rook",
        from_position=Position(0, 0),
        to_position=Position(0, 1),
    )


def test_subscribe_receives_published_events():
    bus = EventBus()
    observer = RecordingObserver()

    bus.subscribe(observer)
    event = make_move_event()
    bus.publish(event)

    assert observer.events == [event]


def test_unsubscribe_stops_delivery():
    bus = EventBus()
    observer = RecordingObserver()

    bus.subscribe(observer)
    bus.unsubscribe(observer)
    bus.publish(make_move_event())

    assert observer.events == []


def test_multiple_observers_receive_same_event():
    bus = EventBus()
    first = RecordingObserver()
    second = RecordingObserver()
    event = make_move_event()

    bus.subscribe(first)
    bus.subscribe(second)
    bus.publish(event)

    assert first.events == [event]
    assert second.events == [event]
