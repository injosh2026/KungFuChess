from dataclasses import replace

from kungfu_chess.snapshot.game_snapshot import GameSnapshot, PieceSnapshot
from kungfu_chess.snapshot.snapshot_source import SnapshotSource
from kungfu_chess.snapshot.visual_position_overlay import (
    index_motions_by_piece_id,
    visual_position_for_piece,
)


class NetworkSnapshotSource(SnapshotSource):
    """
    Provides snapshots received from a remote server.

    The source does not know about networking details.
    It only consumes already received snapshots.

    When a controller is provided, local selection state is overlaid
    onto the latest server snapshot for rendering.

    When motion tracking dependencies are provided, active client motions
    are advanced on each read and merged into a render-only snapshot copy.
    The stored authoritative snapshot is never mutated.
    """

    def __init__(
        self,
        connection,
        controller=None,
        motion_tracker=None,
        animation_clock=None,
        visual_position_calculator=None,
    ):
        self._connection = connection
        self._controller = controller
        self._motion_tracker = motion_tracker
        self._animation_clock = animation_clock
        self._visual_position_calculator = visual_position_calculator
        self._latest_snapshot = None
        self._last_clock_ms = None

    def update(self, snapshot: GameSnapshot) -> None:
        self._latest_snapshot = snapshot

        if self._motion_tracker is not None:
            self._motion_tracker.reconcile(snapshot)

    def get_snapshot(self) -> GameSnapshot | None:
        if self._latest_snapshot is None:
            return None

        self._advance_motion_tracker()

        return self._build_render_snapshot(self._latest_snapshot)

    def _advance_motion_tracker(self) -> None:
        if self._motion_tracker is None or self._animation_clock is None:
            return

        now_ms = self._animation_clock.elapsed_ms()

        if self._last_clock_ms is None:
            self._last_clock_ms = now_ms
            return

        delta_ms = now_ms - self._last_clock_ms
        self._last_clock_ms = now_ms

        if delta_ms > 0:
            self._motion_tracker.advance(delta_ms)

    def _build_render_snapshot(self, snapshot: GameSnapshot) -> GameSnapshot:
        render_snapshot = snapshot

        if self._motion_tracker is not None and self._visual_position_calculator is not None:
            render_snapshot = replace(
                render_snapshot,
                pieces=self._apply_motion_overlay(snapshot.pieces),
            )

        if self._controller is None:
            return render_snapshot

        return replace(
            render_snapshot,
            selected_cell=self._controller.selected_position,
            legal_moves=set(self._controller.legal_moves),
        )

    def _apply_motion_overlay(
        self,
        pieces: list[PieceSnapshot],
    ) -> list[PieceSnapshot]:
        motion_by_piece_id = index_motions_by_piece_id(
            self._motion_tracker.active_motions(),
        )

        overlay_pieces: list[PieceSnapshot] = []

        for piece in pieces:
            visual_position = visual_position_for_piece(
                piece.piece_id,
                motion_by_piece_id,
                self._visual_position_calculator,
            )
            motion_state = self._motion_tracker.motion_state_for(piece.piece_id)

            if visual_position is None and motion_state is None:
                overlay_pieces.append(piece)
                continue

            overlay_pieces.append(
                replace(
                    piece,
                    visual_position=visual_position,
                    state=motion_state if motion_state is not None else piece.state,
                )
            )

        return overlay_pieces
