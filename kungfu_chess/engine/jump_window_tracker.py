from dataclasses import dataclass


@dataclass(slots=True)
class _JumpWindow:
    duration_ms: int
    elapsed_ms: int = 0


class JumpWindowTracker:
    """
    Tracks an in-place jump protection window for a piece.

    The tracker measures elapsed time independently from piece state
    names so collision rules can consult an active jump window without
    relying on animation state strings.
    """

    def __init__(self):
        self._windows: dict[int, _JumpWindow] = {}

    def start(self, piece_id: int, duration_ms: int) -> None:
        self._windows[piece_id] = _JumpWindow(duration_ms=duration_ms)

    def advance(self, milliseconds: int) -> list[int]:
        finished: list[int] = []

        for piece_id, window in self._windows.items():
            window.elapsed_ms += milliseconds
            if window.elapsed_ms >= window.duration_ms:
                finished.append(piece_id)

        for piece_id in finished:
            del self._windows[piece_id]

        return finished

    def is_active_at(self, piece_id: int, additional_elapsed_ms: int) -> bool:
        window = self._windows.get(piece_id)
        if window is None:
            return False

        return window.elapsed_ms + additional_elapsed_ms < window.duration_ms

    def clear(self, piece_id: int) -> None:
        self._windows.pop(piece_id, None)
