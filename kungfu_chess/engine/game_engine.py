from kungfu_chess.config.piece_code import piece_code
from kungfu_chess.config.piece_config_repository import PieceConfigRepository
from kungfu_chess.engine.arrival_resolver import ArrivalResolver
from kungfu_chess.engine.collision_resolver import CollisionResolver
from kungfu_chess.engine.motion_factory import MotionFactory
from kungfu_chess.engine.move_result import MoveResult
from kungfu_chess.engine.state_transition_resolver import StateTransitionResolver
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter
from kungfu_chess.realtime.state_timer import StateTimer
from kungfu_chess.rules.rule_engine import RuleEngine

MAX_PASS_THROUGH_STEPS = 16
PIECE_IN_COOLDOWN = "piece_in_cooldown"
PIECE_IN_MOTION = "piece_in_motion"


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

    def request_move(self, source, destination) -> MoveResult:

        if self.game_state.game_over:
            return MoveResult(False, "game_over")

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
        completed_motions = self.realtime_arbiter.advance_time(milliseconds)

        active_timers = frozenset(self._state_timer.active_piece_ids())

        captured_pieces = []

        sorted_motions = self._collision_resolver.sort_arrivals(completed_motions)

        for motion in sorted_motions:
            self._collision_resolver.resolve_arrival(
                motion,
                self.game_state.board,
            )

            captured = self.arrival_resolver.resolve(motion)

            if captured is not None:
                captured_pieces.append(captured)

            piece = self.game_state.board.pieces_by_id.get(motion.piece_id)
            if piece is not None:
                self._transition_piece(piece)

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
