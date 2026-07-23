from collections.abc import Mapping

from kungfu_chess.engine.services.jump_service import JumpService
from kungfu_chess.engine.services.move_service import MoveService
from kungfu_chess.engine.services.simulation_service import SimulationService
from kungfu_chess.view.runtime_role import RuntimeRole
from kungfu_chess.model.game_state import GameState
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter
from kungfu_chess.realtime.state_timer import StateTimer
from kungfu_chess.rules.rule_engine import RuleEngine


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
        state_timer: StateTimer,
        move_service: MoveService | None = None,
        jump_service: JumpService | None = None,
        simulation_service: SimulationService | None = None,
    ):
        self.game_state = game_state
        self.rule_engine = rule_engine
        self.realtime_arbiter = realtime_arbiter
        self._state_timer = state_timer
        self._game_elapsed_ms = 0
        self._move_service = move_service
        self._jump_service = jump_service
        self._simulation_service = simulation_service

    def request_move(self, source, destination):
        return self._move_service.request_move(
            source,
            destination,
        )

    def request_jump(self, piece_id: int):
        if self._jump_service is None:
            raise RuntimeError("JumpService not configured")
        return self._jump_service.request_jump(piece_id)

    def wait(self, milliseconds):
        return self._simulation_service.advance(milliseconds)

    def active_motions(self):
        """
        Returns all motions currently tracked by the realtime arbiter.

        View layers use this facade instead of accessing the arbiter
        directly.
        """
        return self.realtime_arbiter.active_motions()

    def state_timer_progress(self, piece_id: int) -> float | None:
        return self._state_timer.progress(piece_id)

    def runtime_progress(self, piece_id: int) -> Mapping[RuntimeRole, float]:
        progress: dict[RuntimeRole, float] = {}

        active_ability_progress = (
            self._jump_service.progress(piece_id)
            if self._jump_service is not None
            else None
        )
        if active_ability_progress is not None:
            progress[RuntimeRole.ACTIVE_ABILITY] = active_ability_progress

        recovery_progress = self._state_timer.progress(piece_id)
        if recovery_progress is not None:
            progress[RuntimeRole.RECOVERY] = recovery_progress

        return progress

    def timed_state_progress(self, piece_id: int) -> float | None:
        jump_progress = (
            self._jump_service.progress(piece_id)
            if self._jump_service is not None
            else None
        )
        if jump_progress is not None:
            return jump_progress

        return self._state_timer.progress(piece_id)

    def is_piece_in_cooldown(self, piece_id: int) -> bool:
        return self._state_timer.has_active_timer(piece_id)

    def get_legal_moves(self, position):
        return self.rule_engine.legal_moves(
            self.game_state.board,
            position,
        )
