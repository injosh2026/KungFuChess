from typing import Protocol

from kungfu_chess.events.game_event import GameEvent


class GameObserver(Protocol):
    """
    Receives published game events from an EventBus.

    Observers convert events into their own stored representations.
    They must not mutate engine state.
    """

    def on_game_event(self, event: GameEvent) -> None:
        ...
