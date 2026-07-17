from kungfu_chess.config.piece_code import piece_code
from kungfu_chess.config.piece_config_repository import PieceConfigRepository
from kungfu_chess.engine.arrival_resolver import ArrivalResolver
from kungfu_chess.engine.collision_decisions import (
    STATIONARY_ENTRY_TIME_MS,
    CellEntryEvent,
    CellOccupant,
    EntryOutcome,
    MotionCompletionEvent,
)
from kungfu_chess.engine.collision_resolver import CollisionResolver
from kungfu_chess.engine.motion_factory import MotionFactory
from kungfu_chess.engine.move_result import MoveResult
from kungfu_chess.engine.state_transition_resolver import StateTransitionResolver
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.realtime.motion_kinematics import entry_time_ms
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter
from kungfu_chess.realtime.state_timer import StateTimer
from kungfu_chess.rules.pawn_end_handler import PawnEndHandler
from kungfu_chess.rules.pawn_end_outcome import PendingPawnPromotion
from kungfu_chess.rules.jump_rule import JumpRule
from kungfu_chess.rules.rule_engine import RuleEngine

MAX_PASS_THROUGH_STEPS = 16
PIECE_IN_COOLDOWN = "piece_in_cooldown"
PIECE_IN_MOTION = "piece_in_motion"
PENDING_PAWN_PROMOTION = "pending_pawn_promotion"
NO_PENDING_PAWN_PROMOTION = "no_pending_pawn_promotion"
WRONG_PROMOTION_PIECE = "wrong_promotion_piece"
INVALID_PROMOTION_CHOICE = "invalid_promotion_choice"
PROMOTION_PIECE_NOT_FOUND = "promotion_piece_not_found"
JUMP_PIECE_NOT_FOUND = "jump_piece_not_found"
JUMP_NOT_ALLOWED = "jump_not_allowed"


class GameEngine:
    """
    Coordinates the main game flow.

    GameEngine receives move requests, delegates rule validation,
    creates motions, advances simulated time, and resolves
    completed movements.

    It does not contain piece movement rules, rendering logic,
    or input handling.
    """

    def __init__(
        self,
        game_state: GameState,
        rule_engine: RuleEngine,
        realtime_arbiter: RealTimeArbiter,
        motion_factory: MotionFactory,
        state_transition_resolver: StateTransitionResolver,
        config_repository: PieceConfigRepository,
        state_timer: StateTimer,
        collision_resolver: CollisionResolver | None = None,
        pawn_end_handler: PawnEndHandler | None = None,
        jump_rule: JumpRule | None = None,
    ):
        self.game_state = game_state
        self.rule_engine = rule_engine
        self.realtime_arbiter = realtime_arbiter
        self.arrival_resolver = ArrivalResolver(game_state)
        self.motion_factory = motion_factory
        self._state_transition_resolver = state_transition_resolver
        self._config_repository = config_repository
        self._state_timer = state_timer
        self._collision_resolver = collision_resolver or CollisionResolver()
        self._pawn_end_handler = pawn_end_handler
        self._jump_rule = jump_rule or JumpRule()

    def request_move(self, source, destination) -> MoveResult:

        if self.game_state.game_over:
            return MoveResult(False, "game_over")

        if self.game_state.pending_pawn_promotion is not None:
            return MoveResult(False, PENDING_PAWN_PROMOTION)

        validation = self.rule_engine.validate_move(
            self.game_state.board, source, destination
        )

        if not validation.is_valid:
            return MoveResult(False, validation.reason)

        piece = self.game_state.board.get_piece_by_position(source)

        if piece is None:
            raise RuntimeError("Validated move without source piece")

        if self._state_timer.has_active_timer(piece.id):
            return MoveResult(False, PIECE_IN_COOLDOWN)

        if self.realtime_arbiter.has_motion(piece.id):
            return MoveResult(False, PIECE_IN_MOTION)

        code = piece_code(piece.kind, piece.color)
        piece.state = self._config_repository.get_move_command_state(code)

        motion = self.motion_factory.create(piece, source, destination)

        if not self.realtime_arbiter.start_motion(motion):
            return MoveResult(False, PIECE_IN_MOTION)

        return MoveResult(True, "ok")

    def request_jump(self, piece_id: int) -> MoveResult:
        if self.game_state.game_over:
            return MoveResult(False, "game_over")

        if self.game_state.pending_pawn_promotion is not None:
            return MoveResult(False, PENDING_PAWN_PROMOTION)

        piece = self.game_state.board.get_piece_by_id(piece_id)
        if piece is None:
            return MoveResult(False, JUMP_PIECE_NOT_FOUND)

        if self._state_timer.has_active_timer(piece.id):
            return MoveResult(False, PIECE_IN_COOLDOWN)

        if self.realtime_arbiter.has_motion(piece.id):
            return MoveResult(False, PIECE_IN_MOTION)

        if not self._jump_rule.can_jump(self.game_state, piece):
            return MoveResult(False, JUMP_NOT_ALLOWED)

        code = piece_code(piece.kind, piece.color)
        piece.state = self._config_repository.get_jump_command_state(code)
        self._settle_piece_state(piece)

        return MoveResult(True, "ok")

    def active_motions(self):
        """
        Returns all motions currently tracked by the realtime arbiter.

        View layers use this facade instead of accessing the arbiter
        directly.
        """
        return self.realtime_arbiter.active_motions()

    def wait(self, milliseconds: int):
        """
        Advances simulated game time.

        Completed motions are resolved when their duration expires.
        The board is updated only when motions arrive at their target.
        """
        active_timers = frozenset(self._state_timer.active_piece_ids())

        captured_pieces = []

        active_motions = self.realtime_arbiter.active_motions()
        occupied_cells = self._build_initial_occupied_cells(
            self.game_state.board,
            active_motions,
        )
        events = self._collision_resolver.schedule_timeline_events(
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
                outcome = self._collision_resolver.resolve_entry_event(
                    event,
                    self.game_state.board,
                    occupied_cells,
                    active_motions=self.realtime_arbiter.active_motions(),
                )
                self._apply_entry_outcome(
                    outcome,
                    event,
                    occupied_cells,
                    captured_pieces,
                )
            elif isinstance(event, MotionCompletionEvent):
                self._apply_motion_completion(
                    event,
                    occupied_cells,
                    captured_pieces,
                )

        remaining = milliseconds - elapsed
        if remaining > 0:
            self.realtime_arbiter.advance_time(remaining)
            elapsed += remaining

        assert elapsed == milliseconds

        for piece_id in self._state_timer.advance(
            milliseconds,
            only_piece_ids=active_timers,
        ):
            piece = self.game_state.board.pieces_by_id.get(piece_id)
            if piece is not None:
                self._transition_piece(piece)

        return captured_pieces

    def state_timer_progress(self, piece_id: int) -> float | None:
        return self._state_timer.progress(piece_id)

    def is_piece_in_cooldown(self, piece_id: int) -> bool:
        return self._state_timer.has_active_timer(piece_id)

    def get_legal_moves(self, position):
        return self.rule_engine.legal_moves(
            self.game_state.board,
            position,
        )

    def submit_pawn_promotion_choice(
        self,
        piece_id: int,
        chosen_kind: PieceKind,
    ) -> MoveResult:
        pending = self.game_state.pending_pawn_promotion

        if pending is None:
            return MoveResult(False, NO_PENDING_PAWN_PROMOTION)

        if pending.piece_id != piece_id:
            return MoveResult(False, WRONG_PROMOTION_PIECE)

        if chosen_kind not in pending.allowed_kinds:
            return MoveResult(False, INVALID_PROMOTION_CHOICE)

        piece = self.game_state.board.get_piece_by_id(piece_id)
        if piece is None:
            return MoveResult(False, PROMOTION_PIECE_NOT_FOUND)

        piece.kind = chosen_kind
        piece.state = PieceState.IDLE
        self.game_state.pending_pawn_promotion = None
        self._transition_piece(piece)

        return MoveResult(True, "ok")

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
            victim = self.game_state.board.get_piece_by_id(
                outcome.capture.victim_piece_id
            )
            if victim is not None:
                self.game_state.board.remove_piece(victim.cell)
                self.realtime_arbiter.cancel_motion(victim.id)
                if victim.kind == PieceKind.KING:
                    self.game_state.game_over = True
                captured_pieces.append(victim)

                for cell, occupant in list(occupied_cells.items()):
                    if occupant.piece_id == victim.id:
                        del occupied_cells[cell]

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

    def _apply_motion_completion(
        self,
        event: MotionCompletionEvent,
        occupied_cells: dict[Position, CellOccupant],
        captured_pieces: list[Piece],
    ) -> None:
        if self.game_state.board.get_piece_by_id(event.piece_id) is None:
            return

        motion = self.realtime_arbiter.get_motion(event.piece_id)
        if motion is None:
            motion = event.motion
        else:
            self.realtime_arbiter.cancel_motion(event.piece_id)

        arrival_outcome = self._collision_resolver.resolve_arrival(
            motion,
            self.game_state.board,
        )

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
            blocks_transition = self._apply_pawn_end_outcome(piece, arrival_cell)
            if not blocks_transition:
                self._transition_piece(piece)
            self._set_piece_occupied_cell(
                occupied_cells,
                piece.id,
                piece.color,
                arrival_cell,
                STATIONARY_ENTRY_TIME_MS,
            )

    def _apply_pawn_end_outcome(self, piece: Piece, landing_cell: Position) -> bool:
        if self._pawn_end_handler is None:
            return False

        outcome = self._pawn_end_handler.resolve(
            piece,
            landing_cell,
            self.game_state.board,
        )

        if outcome.pending_choice_kinds is not None:
            self.game_state.pending_pawn_promotion = PendingPawnPromotion(
                piece_id=piece.id,
                allowed_kinds=outcome.pending_choice_kinds,
            )
            return outcome.blocks_state_transition

        if outcome.new_kind is None:
            return False

        piece.kind = outcome.new_kind
        piece.state = PieceState.IDLE
        return outcome.blocks_state_transition

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
        GameEngine._clear_piece_from_occupied_cells(occupied_cells, piece_id)
        occupied_cells[cell] = CellOccupant(
            piece_id=piece_id,
            color=color,
            entry_time_ms=entry_time_ms,
        )

    def _transition_piece(self, piece: Piece) -> None:
        code = piece_code(piece.kind, piece.color)
        piece.state = self._state_transition_resolver.resolve(code, piece.state)
        self._settle_piece_state(piece)

    def _settle_piece_state(self, piece: Piece) -> None:
        code = piece_code(piece.kind, piece.color)

        for _ in range(MAX_PASS_THROUGH_STEPS):
            config = self._config_repository.load_state(code, piece.state)

            if config.physics.duration_ms is not None:
                self._state_timer.start(piece.id, config.physics.duration_ms)
                return

            next_state = self._state_transition_resolver.resolve(
                code,
                piece.state,
            )

            if next_state == piece.state:
                return

            piece.state = next_state
