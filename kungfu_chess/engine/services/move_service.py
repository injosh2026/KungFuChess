from kungfu_chess.config.piece_code import piece_code
from kungfu_chess.config.piece_config_repository import PieceConfigRepository
from kungfu_chess.engine.motion_factory import MotionFactory
from kungfu_chess.engine.move_result import MoveResult
from kungfu_chess.model.game_state import GameState
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter
from kungfu_chess.rules.rule_engine import RuleEngine

PIECE_IN_MOTION = "piece_in_motion"
PIECE_IN_COOLDOWN = "piece_in_cooldown"
PENDING_PAWN_PROMOTION = "pending_pawn_promotion"

class MoveService:

    def __init__(
        self,
        game_state: GameState,
        rule_engine: RuleEngine,
        realtime_arbiter: RealTimeArbiter,
        motion_factory: MotionFactory,
        config_repository: PieceConfigRepository,
    ):
        self.game_state = game_state
        self.rule_engine = rule_engine
        self.realtime_arbiter = realtime_arbiter
        self.motion_factory = motion_factory
        self._config_repository = config_repository

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

        # if self._state_timer.has_active_timer(piece.id):
        #     return MoveResult(False, PIECE_IN_COOLDOWN)

        if self.realtime_arbiter.has_motion(piece.id):
            return MoveResult(False, PIECE_IN_MOTION)

        code = piece_code(piece.kind, piece.color)
        piece.state = self._config_repository.get_move_command_state(code)

        motion = self.motion_factory.create(piece, source, destination)

        if not self.realtime_arbiter.start_motion(motion):
            return MoveResult(False, PIECE_IN_MOTION)

        return MoveResult(True, "ok")
