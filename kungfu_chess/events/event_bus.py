from kungfu_chess.events.game_event import GameEvent
from kungfu_chess.events.game_observer import GameObserver


class EventBus:
    """
    Dispatches game events to subscribed observers.

    The engine owns one instance and publishes domain events without
    knowing which observers are listening.
    """

    def __init__(self) -> None:
        self._observers: list[GameObserver] = []

    def subscribe(self, observer: GameObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: GameObserver) -> None:
        self._observers.remove(observer)

    def publish(self, event: GameEvent) -> None:
        for observer in list(self._observers):
            observer.on_game_event(event)
