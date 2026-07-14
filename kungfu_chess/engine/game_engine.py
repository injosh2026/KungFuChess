from kungfu_chess.engine.arrival_resolver import ArrivalResolver
from kungfu_chess.engine.motion_factory import MotionFactory
from kungfu_chess.engine.move_result import MoveResult
from kungfu_chess.model.game_state import GameState
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter
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
        motion_factory: MotionFactory,
    ):
        self.game_state = game_state
        self.rule_engine = rule_engine
        self.realtime_arbiter = realtime_arbiter
        self.arrival_resolver = ArrivalResolver(game_state)
        self.motion_factory = motion_factory

    def request_move(self, source, destination) -> MoveResult:

        if self.game_state.game_over:
            return MoveResult(False, "game_over")

        if self.realtime_arbiter.has_active_motion():
            return MoveResult(False, "motion_in_progress")

        validation = self.rule_engine.validate_move(
            self.game_state.board, source, destination
        )

        if not validation.is_valid:
            return MoveResult(False, validation.reason)

        piece = self.game_state.board.get_piece_by_position(source)

        if piece is None:
            raise RuntimeError("Validated move without source piece")

        motion = self.motion_factory.create(piece, source, destination)

        self.realtime_arbiter.start_motion(motion)

        return MoveResult(True, "ok")

    def wait(self, milliseconds: int):
        """
        Advances simulated game time.

        Completed motions are resolved when their duration expires.
        The board is updated only when motions arrive at their target.
        """
        completed_motions = self.realtime_arbiter.advance_time(milliseconds)

        captured_pieces = []

        for motion in completed_motions:
            captured = self.arrival_resolver.resolve(motion)

            if captured is not None:
                captured_pieces.append(captured)

        return captured_pieces
