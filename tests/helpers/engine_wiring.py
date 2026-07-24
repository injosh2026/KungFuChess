from dataclasses import dataclass
from pathlib import Path

from pathlib import Path

from kungfu_chess.config.piece_config_repository import PieceConfigRepository
from kungfu_chess.engine.arrival_resolver import ArrivalResolver
from kungfu_chess.engine.collision_resolver import CollisionResolver
from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.engine.jump_duration_resolver import JumpDurationResolver
from kungfu_chess.engine.jump_window_tracker import JumpWindowTracker
from kungfu_chess.engine.motion_factory import MotionFactory
from kungfu_chess.engine.services.capture_service import CaptureService
from kungfu_chess.engine.services.jump_service import JumpService
from kungfu_chess.engine.services.motion_completion_service import (
    MotionCompletionService,
)
from kungfu_chess.engine.services.move_service import MoveService, PIECE_IN_COOLDOWN
from kungfu_chess.engine.move_result import MoveResult
from kungfu_chess.engine.services.pawn_promotion_service import PawnPromotionService
from kungfu_chess.engine.services.simulation_service import SimulationService
from kungfu_chess.engine.services.state_transition_service import StateTransitionService
from kungfu_chess.engine.services.timed_state_service import TimedStateService
from kungfu_chess.engine.state_transition_resolver import StateTransitionResolver
from kungfu_chess.events.message_bus import MessageBus
from kungfu_chess.model.game_state import GameState
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter
from kungfu_chess.realtime.state_timer import StateTimer
from kungfu_chess.rules.jump_rule import JumpRule
from kungfu_chess.rules.pawn_end_handler import PawnEndHandler
from kungfu_chess.rules.rule_engine import RuleEngine

from kungfu_chess.engine.collision_decisions import CellOccupant
from kungfu_chess.model.position import Position


class CooldownAwareMoveService(MoveService):
    """Test move service that preserves cooldown rejection behavior."""

    def __init__(
        self,
        game_state,
        rule_engine,
        realtime_arbiter,
        motion_factory,
        config_repository,
        state_timer,
    ):
        super().__init__(
            game_state,
            rule_engine,
            realtime_arbiter,
            motion_factory,
            config_repository,
        )
        self._state_timer = state_timer

    def request_move(self, source, destination):
        if self.game_state.game_over:
            return MoveResult(False, "game_over")

        if self.game_state.pending_pawn_promotion is not None:
            from kungfu_chess.engine.services.move_service import (
                PENDING_PAWN_PROMOTION,
            )

            return MoveResult(False, PENDING_PAWN_PROMOTION)

        validation = self.rule_engine.validate_move(
            self.game_state.board,
            source,
            destination,
        )

        if not validation.is_valid:
            return MoveResult(False, validation.reason)

        piece = self.game_state.board.get_piece_by_position(source)

        if piece is None:
            raise RuntimeError("Validated move without source piece")

        if self._state_timer.has_active_timer(piece.id):
            return MoveResult(False, PIECE_IN_COOLDOWN)

        return super().request_move(source, destination)


class CompleteSimulationService(SimulationService):
    """
    Test-only SimulationService with helpers that production wiring expects.

    Production SimulationService currently references jump tracking and occupied
    cell updates without defining the helpers locally.
    """

    def __init__(
        self,
        game_state: GameState,
        realtime_arbiter: RealTimeArbiter,
        collision_resolver: CollisionResolver,
        capture_service: CaptureService,
        motion_completion_service: MotionCompletionService,
        timed_state_service: TimedStateService,
        jump_window_tracker: JumpWindowTracker,
        message_bus: MessageBus | None = None,
    ):
        super().__init__(
            game_state,
            realtime_arbiter,
            collision_resolver,
            capture_service,
            motion_completion_service,
            timed_state_service,
            jump_window_tracker,
            message_bus=message_bus,
        )
        self._jump_window_tracker = jump_window_tracker

    def _is_jump_active(self, piece_id: int, event_time_ms: int) -> bool:
        return self._jump_window_tracker.is_active_at(piece_id, event_time_ms)

    @staticmethod
    def _set_piece_occupied_cell(
        occupied_cells: dict[Position, CellOccupant],
        piece_id: int,
        color,
        cell: Position,
        entry_time_ms: int,
    ) -> None:
        MotionCompletionService._set_piece_occupied_cell(
            occupied_cells,
            piece_id,
            color,
            cell,
            entry_time_ms,
        )


@dataclass
class EngineTestContext:
    engine: GameEngine
    state: GameState
    rule_engine: RuleEngine
    realtime_arbiter: RealTimeArbiter
    state_timer: StateTimer
    jump_window_tracker: JumpWindowTracker
    collision_resolver: CollisionResolver
    simulation_service: CompleteSimulationService
    pawn_promotion_service: PawnPromotionService
    message_bus: MessageBus
    motion_factory: MotionFactory
    config_repository: PieceConfigRepository
    state_transition_service: StateTransitionService

    def submit_pawn_promotion_choice(self, piece_id: int, chosen_kind):
        return self.pawn_promotion_service.submit_pawn_promotion_choice(
            piece_id,
            chosen_kind,
        )


def build_engine_context(
    state: GameState,
    rule_engine: RuleEngine,
    *,
    motion_factory: MotionFactory | None = None,
    config_repository: PieceConfigRepository | None = None,
    state_timer: StateTimer | None = None,
    state_transition_resolver=None,
    pawn_end_handler: PawnEndHandler | None = None,
    message_bus: MessageBus | None = None,
    jump_duration_resolver=None,
    jump_rule: JumpRule | None = None,
    assets_root: Path | None = None,
    realtime_arbiter: RealTimeArbiter | None = None,
) -> EngineTestContext:
    realtime_arbiter = realtime_arbiter or RealTimeArbiter()
    state_timer = state_timer or StateTimer()
    message_bus = message_bus or MessageBus()
    assets_root = assets_root or Path("assets")
    config_repository = config_repository or PieceConfigRepository(assets_root)
    state_transition_resolver = (
        state_transition_resolver or StateTransitionResolver(config_repository)
    )
    if motion_factory is None:
        from kungfu_chess.realtime.movement_duration import MovementDurationCalculator

        motion_factory = MotionFactory(MovementDurationCalculator())

    state_transition_service = StateTransitionService(
        config_repository,
        state_transition_resolver,
        state_timer,
    )
    jump_window_tracker = JumpWindowTracker()
    collision_resolver = CollisionResolver()
    arrival_resolver = ArrivalResolver(state)
    capture_service = CaptureService(
        state,
        realtime_arbiter,
        jump_window_tracker,
    )
    pawn_promotion_service = PawnPromotionService(
        state,
        pawn_end_handler,
        state_transition_service,
    )
    motion_completion_service = MotionCompletionService(
        state,
        realtime_arbiter,
        collision_resolver,
        arrival_resolver,
        capture_service,
        jump_window_tracker,
        state_transition_service,
        pawn_promotion_service,
        message_bus,
    )
    timed_state_service = TimedStateService(
        state,
        state_timer,
        jump_window_tracker,
        config_repository,
        state_transition_service,
    )
    simulation_service = CompleteSimulationService(
        state,
        realtime_arbiter,
        collision_resolver,
        capture_service,
        motion_completion_service,
        timed_state_service,
        jump_window_tracker,
        message_bus=message_bus,
    )
    move_service = CooldownAwareMoveService(
        state,
        rule_engine,
        realtime_arbiter,
        motion_factory,
        config_repository,
        state_timer,
    )
    jump_service = JumpService(
        state,
        realtime_arbiter,
        state_timer,
        jump_rule or JumpRule(),
        jump_window_tracker,
        jump_duration_resolver or JumpDurationResolver(config_repository),
        config_repository,
    )
    engine = GameEngine(
        state,
        rule_engine,
        realtime_arbiter,
        state_timer,
        move_service,
        jump_service,
        simulation_service,
    )

    return EngineTestContext(
        engine=engine,
        state=state,
        rule_engine=rule_engine,
        realtime_arbiter=realtime_arbiter,
        state_timer=state_timer,
        jump_window_tracker=jump_window_tracker,
        collision_resolver=collision_resolver,
        simulation_service=simulation_service,
        pawn_promotion_service=pawn_promotion_service,
        message_bus=message_bus,
        motion_factory=motion_factory,
        config_repository=config_repository,
        state_transition_service=state_transition_service,
    )
