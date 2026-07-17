from collections.abc import Callable

from kungfu_chess.engine.collision_decisions import (
    ENTRY_EVENT_PRIORITY,
    COMPLETION_EVENT_PRIORITY,
    ArrivalOutcome,
    CaptureAtArrival,
    CellEntryEvent,
    EntryOutcome,
    MotionCompletionEvent,
)
from kungfu_chess.model.board import Board
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.realtime.motion_kinematics import (
    build_path,
    entry_time_ms,
    mid_path_indices,
)


JumpActiveCheck = Callable[[int, int], bool]


class CollisionResolver:
    """
    Applies Kung Fu Chess arrival collision rules.

    CollisionResolver is stateless. It inspects the board and returns
    decisions only. It never mutates game state.
    """

    def sort_arrivals(self, completed: list[Motion]) -> tuple[Motion, ...]:
        """
        Orders completed motions for sequential arrival processing.

        Earlier entries arrive first. Later entries may capture occupants
        placed by earlier arrivals at the same cell.

        Sort key:
            1. motion.duration_ms (relative completion time)
            2. motion.piece_id (deterministic tie-break)
        """
        return tuple(
            sorted(
                completed,
                key=lambda motion: (motion.duration_ms, motion.piece_id),
            )
        )

    def resolve_arrival(
        self,
        motion: Motion,
        board: Board,
        *,
        is_jump_active: JumpActiveCheck | None = None,
        event_time_ms: int = 0,
    ) -> ArrivalOutcome:
        """
        Inspects the target cell before an arrival is applied.

        Args:
            motion:
                Completed motion about to be resolved.
            board:
                Current logical board state.

        Returns:
            ArrivalOutcome describing capture and the resolved landing cell.
        """
        occupant = board.get_piece_by_position(motion.target)

        if occupant is None:
            return ArrivalOutcome()

        mover = board.get_piece_by_id(motion.piece_id)

        if mover is None:
            return ArrivalOutcome()

        if occupant.color != mover.color:
            if is_jump_active is not None and is_jump_active(
                occupant.id,
                event_time_ms,
            ):
                return ArrivalOutcome(
                    capture=CaptureAtArrival(
                        capturer_piece_id=occupant.id,
                        victim_piece_id=motion.piece_id,
                        at_cell=motion.target,
                    )
                )

            return ArrivalOutcome(
                capture=CaptureAtArrival(
                    capturer_piece_id=motion.piece_id,
                    victim_piece_id=occupant.id,
                    at_cell=motion.target,
                )
            )

        return self._resolve_friendly_blocked_arrival(motion, board, mover)

    def _resolve_friendly_blocked_arrival(
        self,
        motion: Motion,
        board: Board,
        mover,
    ) -> ArrivalOutcome:
        path = self._path_for_motion(motion, board)

        for path_index in range(len(path) - 2, -1, -1):
            cell = path[path_index]
            cell_occupant = board.get_piece_by_position(cell)

            if cell_occupant is None or cell_occupant.id == mover.id:
                return ArrivalOutcome(arrival_cell=cell)

            if cell_occupant.color == mover.color:
                continue

            return ArrivalOutcome(
                capture=CaptureAtArrival(
                    capturer_piece_id=motion.piece_id,
                    victim_piece_id=cell_occupant.id,
                    at_cell=cell,
                ),
                arrival_cell=cell,
            )

        return ArrivalOutcome(arrival_cell=motion.start)

    def schedule_timeline_events(
        self,
        board: Board,
        motions: tuple[Motion, ...],
        *,
        within_ms: int,
    ) -> tuple[CellEntryEvent | MotionCompletionEvent, ...]:
        """
        Schedules mid-path entries and motion completions within a wait window.

        Event times are relative to the start of the current wait call.
        """
        events: list[CellEntryEvent | MotionCompletionEvent] = []

        for motion in motions:
            completion_time = motion.duration_ms - motion.elapsed_ms
            if 0 < completion_time <= within_ms:
                events.append(
                    MotionCompletionEvent(
                        piece_id=motion.piece_id,
                        motion=motion,
                        time_from_wait_start_ms=completion_time,
                    )
                )

            path = self._path_for_motion(motion, board)
            for path_index in mid_path_indices(path):
                absolute_entry_time = entry_time_ms(path_index)
                time_from_wait_start = absolute_entry_time - motion.elapsed_ms
                if 0 < time_from_wait_start <= within_ms:
                    events.append(
                        CellEntryEvent(
                            piece_id=motion.piece_id,
                            cell=path[path_index],
                            time_from_wait_start_ms=time_from_wait_start,
                            motion=motion,
                            path_index=path_index,
                        )
                    )

        events.sort(
            key=lambda event: (
                event.time_from_wait_start_ms,
                ENTRY_EVENT_PRIORITY
                if isinstance(event, CellEntryEvent)
                else COMPLETION_EVENT_PRIORITY,
                event.piece_id,
            )
        )

        return tuple(events)

    def resolve_entry_event(
        self,
        event: CellEntryEvent,
        board: Board,
        occupied_cells: dict,
        *,
        active_motions: tuple[Motion, ...] = (),
        is_jump_active: JumpActiveCheck | None = None,
    ) -> EntryOutcome:
        """
        Inspects a cell entry against current logical occupancy.

        Args:
            event:
                Scheduled cell entry event.
            board:
                Current logical board state.
            occupied_cells:
                Read-only snapshot of current cell occupants.
            active_motions:
                Active motions at the event time, used for path-based
                crossing and head-on collision detection.

        Returns:
            EntryOutcome describing whether an enemy capture should occur.
        """
        mover = board.get_piece_by_id(event.piece_id)
        if mover is None:
            return EntryOutcome()

        occupant = occupied_cells.get(event.cell)
        if occupant is not None and occupant.color != mover.color:
            if is_jump_active is not None and is_jump_active(
                occupant.piece_id,
                event.time_from_wait_start_ms,
            ):
                return EntryOutcome(
                    capture=CaptureAtArrival(
                        capturer_piece_id=occupant.piece_id,
                        victim_piece_id=event.piece_id,
                        at_cell=event.cell,
                    )
                )

            return EntryOutcome(
                capture=CaptureAtArrival(
                    capturer_piece_id=event.piece_id,
                    victim_piece_id=occupant.piece_id,
                    at_cell=event.cell,
                )
            )

        crossing_victim_id = self._find_crossing_path_victim_id(
            event,
            board,
            active_motions,
            mover,
        )
        if crossing_victim_id is not None:
            return EntryOutcome(
                capture=CaptureAtArrival(
                    capturer_piece_id=event.piece_id,
                    victim_piece_id=crossing_victim_id,
                    at_cell=event.cell,
                )
            )

        head_on_victim_id = self._find_head_on_victim_id(
            event,
            board,
            active_motions,
            mover,
        )
        if head_on_victim_id is not None:
            return EntryOutcome(
                capture=CaptureAtArrival(
                    capturer_piece_id=event.piece_id,
                    victim_piece_id=head_on_victim_id,
                    at_cell=event.cell,
                )
            )

        return EntryOutcome()

    def _find_crossing_path_victim_id(
        self,
        event: CellEntryEvent,
        board: Board,
        active_motions: tuple[Motion, ...],
        mover,
    ) -> int | None:
        """
        Returns an enemy piece id whose active motion has already reached
        the entered cell on a non-opposing (crossing) path.
        """
        candidates: list[int] = []

        for motion in active_motions:
            if motion.piece_id == mover.id:
                continue

            if self._are_opposing_collinear(event.motion, motion, board):
                continue

            victim_id = self._motion_path_victim_at_cell(
                motion,
                event.cell,
                board,
                mover.color,
            )
            if victim_id is not None:
                candidates.append(victim_id)

        if not candidates:
            return None

        return min(candidates)

    def _find_head_on_victim_id(
        self,
        event: CellEntryEvent,
        board: Board,
        active_motions: tuple[Motion, ...],
        mover,
    ) -> int | None:
        """
        Returns an enemy piece id for a head-on encounter on the same line.
        """
        candidates: list[int] = []

        for motion in active_motions:
            if motion.piece_id == mover.id:
                continue

            if not self._are_opposing_collinear(event.motion, motion, board):
                continue

            victim_id = self._motion_path_victim_at_cell(
                motion,
                event.cell,
                board,
                mover.color,
            )
            if victim_id is not None:
                candidates.append(victim_id)

        if not candidates:
            return None

        return min(candidates)

    def _motion_path_victim_at_cell(
        self,
        motion: Motion,
        cell: Position,
        board: Board,
        mover_color,
    ) -> int | None:
        piece = board.get_piece_by_id(motion.piece_id)
        if piece is None or piece.color == mover_color:
            return None

        path = self._path_for_motion(motion, board)
        try:
            path_index = path.index(cell)
        except ValueError:
            return None

        if motion.elapsed_ms < entry_time_ms(path_index):
            return None

        return motion.piece_id

    def _are_opposing_collinear(
        self,
        motion_a: Motion,
        motion_b: Motion,
        board: Board,
    ) -> bool:
        path_a = self._path_for_motion(motion_a, board)
        path_b = self._path_for_motion(motion_b, board)

        if len(path_a) < 2 or len(path_b) < 2:
            return False

        shared_cells = set(path_a) & set(path_b)
        if len(shared_cells) < 2:
            return False

        delta_a = (
            motion_a.target.row - motion_a.start.row,
            motion_a.target.col - motion_a.start.col,
        )
        delta_b = (
            motion_b.target.row - motion_b.start.row,
            motion_b.target.col - motion_b.start.col,
        )

        dot_product = delta_a[0] * delta_b[0] + delta_a[1] * delta_b[1]
        return dot_product < 0

    def _path_for_motion(
        self,
        motion: Motion,
        board: Board,
    ) -> tuple[Position, ...]:
        piece = board.get_piece_by_id(motion.piece_id)
        if piece is None:
            return (motion.start, motion.target)

        if piece.kind == PieceKind.KNIGHT:
            return (motion.start, motion.target)

        try:
            return build_path(motion.start, motion.target)
        except ValueError:
            return (motion.start, motion.target)
