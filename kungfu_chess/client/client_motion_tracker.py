from dataclasses import dataclass

from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.snapshot.game_snapshot import GameSnapshot


@dataclass(slots=True)
class TrackedMotion:
    motion: Motion
    state: str


class ClientMotionTracker:
    """
    Presentation-only tracker for client-side motion interpolation.

    Stores active motions and their render states. It never mutates the
    authoritative board or applies game rules.
    """

    def __init__(self):
        self._tracked_motions: dict[int, TrackedMotion] = {}
        self._authoritative_positions: dict[int, Position] = {}

    def start(self, motion: Motion, state: str) -> None:
        authoritative_position = self._authoritative_positions.get(motion.piece_id)
        if (
            authoritative_position is not None
            and authoritative_position == motion.target
        ):
            return

        self._tracked_motions[motion.piece_id] = TrackedMotion(
            motion=motion,
            state=state,
        )

    def advance(self, delta_ms: int) -> None:
        if delta_ms <= 0:
            return

        for tracked in self._tracked_motions.values():
            motion = tracked.motion
            remaining_ms = motion.duration_ms - motion.elapsed_ms
            if remaining_ms <= 0:
                continue

            motion.advance_time(min(delta_ms, remaining_ms))

    def reconcile(self, snapshot: GameSnapshot) -> None:
        self._authoritative_positions = {
            piece.piece_id: piece.position
            for piece in snapshot.pieces
        }

        for piece_id, tracked in list(self._tracked_motions.items()):
            authoritative_position = self._authoritative_positions.get(piece_id)

            if authoritative_position is None:
                del self._tracked_motions[piece_id]
                continue

            if authoritative_position == tracked.motion.target:
                del self._tracked_motions[piece_id]

    def active_motions(self) -> tuple[Motion, ...]:
        return tuple(
            tracked.motion
            for tracked in self._tracked_motions.values()
        )

    def motion_state_for(self, piece_id: int) -> str | None:
        tracked = self._tracked_motions.get(piece_id)
        if tracked is None:
            return None

        return tracked.state
