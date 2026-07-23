from kungfu_chess.config.piece_code import piece_code
from kungfu_chess.config.piece_config_repository import PieceConfigRepository
from kungfu_chess.engine.jump_duration_resolver import JumpDurationResolver
from kungfu_chess.engine.jump_window_tracker import JumpWindowTracker
from kungfu_chess.engine.move_result import MoveResult
from kungfu_chess.model.game_state import GameState
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter
from kungfu_chess.realtime.state_timer import StateTimer
from kungfu_chess.rules.jump_rule import JumpRule

PIECE_IN_COOLDOWN = "piece_in_cooldown"
PIECE_IN_MOTION = "piece_in_motion"
PENDING_PAWN_PROMOTION = "pending_pawn_promotion"
JUMP_PIECE_NOT_FOUND = "jump_piece_not_found"
JUMP_NOT_ALLOWED = "jump_not_allowed"


class JumpService:

    def __init__(
        self,
        game_state: GameState,
        realtime_arbiter: RealTimeArbiter,
        state_timer: StateTimer,
        jump_rule: JumpRule,
        jump_window_tracker: JumpWindowTracker,
        jump_duration_resolver: JumpDurationResolver,
        config_repository: PieceConfigRepository,
    ):
        self._game_state = game_state
        self._realtime_arbiter = realtime_arbiter
        self._state_timer  = state_timer
        self._jump_rule = jump_rule
        self._jump_window_tracker = jump_window_tracker
        self._jump_duration_resolver = jump_duration_resolver
        self._config_repository = config_repository

    def request_jump(self, piece_id: int) -> MoveResult:

        if self._game_state.game_over:
            return MoveResult(False, "game_over")

        if self._game_state.pending_pawn_promotion is not None:
            return MoveResult(False, PENDING_PAWN_PROMOTION)

        piece = self._game_state.board.get_piece_by_id(piece_id)

        if piece is None:
            return MoveResult(False, JUMP_PIECE_NOT_FOUND)

        if self._state_timer.has_active_timer(piece.id):
            return MoveResult(False, PIECE_IN_COOLDOWN)

        if self._realtime_arbiter.has_motion(piece.id):
            return MoveResult(False, PIECE_IN_MOTION)

        if not self._jump_rule.can_jump(
            self._game_state,
            piece,
        ):
            return MoveResult(False, JUMP_NOT_ALLOWED)

        if self._jump_window_tracker.is_active_at(
            piece.id,
            0,
        ):
            return MoveResult(False, PIECE_IN_COOLDOWN)

        code = piece_code(
            piece.kind,
            piece.color,
        )

        jump_state = self._config_repository.get_jump_command_state(code)

        piece.state = jump_state

        duration_ms = self._jump_duration_resolver.duration_ms(
            code,
            jump_state,
        )

        self._jump_window_tracker.start(
            piece.id,
            duration_ms,
        )

        return MoveResult(True, "ok")

    def progress(self, piece_id: int) -> float | None:
        return self._jump_window_tracker.progress(piece_id)