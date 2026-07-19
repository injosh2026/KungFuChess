from kungfu_chess.events.game_event import GameEvent
from kungfu_chess.events.move_performed_event import MovePerformedEvent
from kungfu_chess.io.square_notation import position_to_square
from kungfu_chess.view.move_history_entry import MoveHistoryEntry


class MoveHistoryObserver:
    """
    Records completed moves from MovePerformedEvent instances.

    The observer owns chronological history. The engine publishes events
    but does not store move history.
    """

    def __init__(self) -> None:
        self._entries: list[MoveHistoryEntry] = []

    def on_game_event(self, event: GameEvent) -> None:
        if not isinstance(event, MovePerformedEvent):
            return

        self._entries.append(
            MoveHistoryEntry(
                elapsed_time_ms=event.timestamp_ms,
                piece_code=event.piece_code,
                piece_name=event.piece_name,
                from_square=position_to_square(event.from_position),
                to_square=position_to_square(event.to_position),
                was_capture=event.capture is not None,
                promotion=event.promotion,
                jump=event.jump_used,
            )
        )

    def entries(self) -> tuple[MoveHistoryEntry, ...]:
        return tuple(self._entries)
