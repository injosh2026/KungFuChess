from kungfu_chess.engine.collision_decisions import (
    STATIONARY_ENTRY_TIME_MS,
    CellEntryEvent,
    CellOccupant,
    EntryOutcome,
    MotionCompletionEvent,
)
from kungfu_chess.engine.collision_resolver import CollisionResolver
from kungfu_chess.engine.services.capture_service import CaptureService
from kungfu_chess.engine.services.motion_completion_service import (
    MotionCompletionService,
)
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.realtime.motion_kinematics import entry_time_ms
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter


class SimulationService:

    def __init__(
        self,
        game_state: GameState,
        realtime_arbiter: RealTimeArbiter,
        collision_resolver: CollisionResolver,
        capture_service: CaptureService,
        motion_completion_service: MotionCompletionService,
        timed_state_service,
        message_bus=None,
    ):
        self.game_state = game_state
        self.realtime_arbiter = realtime_arbiter
        self.collision_resolver = collision_resolver
        self._capture_service = capture_service
        self._motion_completion_service = motion_completion_service
        self._timed_state_service = timed_state_service
        self.message_bus = message_bus
        self._game_elapsed_ms = 0

    def advance(self, milliseconds: int):
        """
        Advances simulated game time.

        Completed motions are resolved when their duration expires.
        The board is updated only when motions arrive at their target.
        """

        self._game_elapsed_ms += milliseconds

        captured_pieces = []

        active_motions = self.realtime_arbiter.active_motions()
        occupied_cells = self._build_initial_occupied_cells(
            self.game_state.board,
            active_motions,
        )
        events = self.collision_resolver.schedule_timeline_events(
            self.game_state.board,
            active_motions,
            within_ms=milliseconds,
        )

        elapsed = 0

        for event in events:
            step = event.time_from_wait_start_ms - elapsed
            if step > 0:
                self.realtime_arbiter.advance_time(step)
                elapsed = event.time_from_wait_start_ms

            if isinstance(event, CellEntryEvent):
                outcome = self.collision_resolver.resolve_entry_event(
                    event,
                    self.game_state.board,
                    occupied_cells,
                    active_motions=self.realtime_arbiter.active_motions(),
                    is_jump_active=self._is_jump_active,
                )
                self._apply_entry_outcome(
                    outcome,
                    event,
                    occupied_cells,
                    captured_pieces,
                )
            elif isinstance(event, MotionCompletionEvent):
                self._motion_completion_service.complete(
                    event,
                    occupied_cells,
                    captured_pieces,
                    self._game_elapsed_ms,
                )

        remaining = milliseconds - elapsed
        if remaining > 0:
            self.realtime_arbiter.advance_time(remaining)
            elapsed += remaining

        assert elapsed == milliseconds

        self._timed_state_service.advance(milliseconds)

        return captured_pieces

    @staticmethod
    def _build_initial_occupied_cells(
        board: Board,
        motions: tuple[Motion, ...],
    ) -> dict[Position, CellOccupant]:
        motion_starts = {motion.piece_id: motion.start for motion in motions}

        occupied_cells: dict[Position, CellOccupant] = {}
        for piece in board.pieces_by_id.values():
            cell = motion_starts.get(piece.id, piece.cell)
            occupied_cells[cell] = CellOccupant(
                piece_id=piece.id,
                color=piece.color,
                entry_time_ms=STATIONARY_ENTRY_TIME_MS,
            )

        return occupied_cells

    def _apply_entry_outcome(
        self,
        outcome: EntryOutcome,
        event: CellEntryEvent,
        occupied_cells: dict[Position, CellOccupant],
        captured_pieces: list[Piece],
    ) -> None:
        if outcome.capture is not None:
            self._capture_service.capture(
                outcome.capture.victim_piece_id,
                occupied_cells,
                captured_pieces,
            )

            if outcome.capture.capturer_piece_id != event.piece_id:
                return

        capturer = self.game_state.board.get_piece_by_id(event.piece_id)
        if capturer is None:
            return

        self._set_piece_occupied_cell(
            occupied_cells,
            event.piece_id,
            capturer.color,
            event.cell,
            entry_time_ms(event.path_index),
        )
