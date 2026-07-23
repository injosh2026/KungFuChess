from kungfu_chess.config.piece_code import piece_code
from kungfu_chess.engine.collision_decisions import (
    STATIONARY_ENTRY_TIME_MS,
    CellOccupant,
    MotionCompletionEvent,
)
from kungfu_chess.events.move_performed_event import MovePerformedEvent
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion


class MotionCompletionService:

    def __init__(
        self,
        game_state,
        realtime_arbiter,
        collision_resolver,
        arrival_resolver,
        capture_service,
        jump_window_tracker,
        state_transition_service,
        pawn_promotion_service,
        message_bus=None,
    ):
        self.game_state = game_state
        self.realtime_arbiter = realtime_arbiter
        self.collision_resolver = collision_resolver
        self.arrival_resolver = arrival_resolver
        self._capture_service = capture_service
        self._jump_window_tracker = jump_window_tracker
        self._state_transition_service = state_transition_service
        self._pawn_promotion_service = pawn_promotion_service
        self.message_bus = message_bus

    def complete(
        self,
        event: MotionCompletionEvent,
        occupied_cells: dict[Position, CellOccupant],
        captured_pieces: list[Piece],
        timestamp_ms,
    ) -> None:

        if self.game_state.board.get_piece_by_id(event.piece_id) is None:
            return

        motion = self.realtime_arbiter.get_motion(event.piece_id)
        if motion is None:
            motion = event.motion
        else:
            self.realtime_arbiter.cancel_motion(event.piece_id)

        arrival_outcome = self.collision_resolver.resolve_arrival(
            motion,
            self.game_state.board,
            is_jump_active=self._is_jump_active,
            event_time_ms=event.time_from_wait_start_ms,
        )

        if (
            arrival_outcome.capture is not None
            and arrival_outcome.capture.capturer_piece_id != motion.piece_id
        ):
            self._capture_service.capture(
                arrival_outcome.capture.victim_piece_id,
                occupied_cells,
                captured_pieces,
            )
            return

        arrival_cell = (
            arrival_outcome.arrival_cell
            if arrival_outcome.arrival_cell is not None
            else motion.target
        )

        captured = self.arrival_resolver.resolve(
            motion,
            arrival_cell=arrival_outcome.arrival_cell,
        )

        if captured is not None:
            captured_pieces.append(captured)

        piece = self.game_state.board.pieces_by_id.get(motion.piece_id)
        if piece is not None:
            piece.has_moved = True
            blocks_transition, promotion_kind = (
                self._pawn_promotion_service.apply_arrival(
                    piece,
                    arrival_cell,
                )
            )
            if not blocks_transition:
                self._state_transition_service.transition(piece)
            self._set_piece_occupied_cell(
                occupied_cells,
                piece.id,
                piece.color,
                arrival_cell,
                STATIONARY_ENTRY_TIME_MS,
            )
            self._publish_move_performed(
                motion=motion,
                arrival_cell=arrival_cell,
                captured=captured,
                promotion_kind=promotion_kind,
                timestamp_ms=timestamp_ms,
            )

    def _is_jump_active(self, piece_id: int, event_time_ms: int) -> bool:
        return self._jump_window_tracker.is_active_at(piece_id, event_time_ms)

    @staticmethod
    def _clear_piece_from_occupied_cells(
        occupied_cells: dict[Position, CellOccupant],
        piece_id: int,
    ) -> None:
        for cell, occupant in list(occupied_cells.items()):
            if occupant.piece_id == piece_id:
                del occupied_cells[cell]

    @staticmethod
    def _set_piece_occupied_cell(
        occupied_cells: dict[Position, CellOccupant],
        piece_id: int,
        color,
        cell: Position,
        entry_time_ms: int,
    ) -> None:
        MotionCompletionService._clear_piece_from_occupied_cells(
            occupied_cells, piece_id
        )
        occupied_cells[cell] = CellOccupant(
            piece_id=piece_id,
            color=color,
            entry_time_ms=entry_time_ms,
        )

    def _publish_move_performed(
        self,
        *,
        motion: Motion,
        arrival_cell: Position,
        captured: Piece | None,
        promotion_kind: PieceKind | None,
        timestamp_ms,
    ) -> None:
        piece = self.game_state.board.get_piece_by_id(motion.piece_id)
        if piece is None:
            return

        capture_code = None
        if captured is not None:
            capture_code = piece_code(captured.kind, captured.color)

        promotion = promotion_kind.value if promotion_kind is not None else None

        self.message_bus.publish(
            MovePerformedEvent(
                timestamp_ms=timestamp_ms,
                piece_id=piece.id,
                piece_code=piece_code(piece.kind, piece.color),
                piece_name=piece.kind.value,
                from_position=motion.start,
                to_position=arrival_cell,
                capture=capture_code,
                promotion=promotion,
                jump_used=False,
            )
        )
