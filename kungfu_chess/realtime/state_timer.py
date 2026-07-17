from dataclasses import dataclass


@dataclass(slots=True)
class _TimerEntry:
    duration_ms: int
    elapsed_ms: int = 0


class StateTimer:
    """
    Tracks elapsed time for timed piece states.

    StateTimer measures cooldown duration only. It does not know piece
    state names or decide transitions.
    """

    def __init__(self):
        self._entries: dict[int, _TimerEntry] = {}

    def start(self, piece_id: int, duration_ms: int) -> None:
        self._entries[piece_id] = _TimerEntry(duration_ms=duration_ms)

    def advance(
        self,
        milliseconds: int,
        *,
        only_piece_ids: frozenset[int] | None = None,
    ) -> list[int]:
        finished: list[int] = []

        for piece_id, entry in self._entries.items():
            if only_piece_ids is not None and piece_id not in only_piece_ids:
                continue

            entry.elapsed_ms += milliseconds
            if entry.elapsed_ms >= entry.duration_ms:
                finished.append(piece_id)

        for piece_id in finished:
            del self._entries[piece_id]

        return finished

    def active_piece_ids(self) -> list[int]:
        return list(self._entries.keys())

    def has_active_timer(self, piece_id: int) -> bool:
        return piece_id in self._entries

    def progress(self, piece_id: int) -> float | None:
        entry = self._entries.get(piece_id)
        if entry is None:
            return None

        if entry.duration_ms <= 0:
            return 1.0

        return min(entry.elapsed_ms / entry.duration_ms, 1.0)
