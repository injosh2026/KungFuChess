from pathlib import Path

from kungfu_chess.config.piece_config_repository import PieceConfigRepository
from kungfu_chess.engine.collision_resolver import CollisionResolver
from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.engine.motion_factory import MotionFactory
from kungfu_chess.engine.state_transition_resolver import StateTransitionResolver
from kungfu_chess.events.event_bus import EventBus
from kungfu_chess.history.move_history_observer import MoveHistoryObserver
from kungfu_chess.scoring.score_observer import ScoreObserver
from kungfu_chess.input.board_mapper import BoardMapper
from kungfu_chess.input.controller import Controller
from kungfu_chess.model.game_state import GameState
from kungfu_chess.realtime.movement_duration import MovementDurationCalculator
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter
from kungfu_chess.realtime.state_timer import StateTimer
from kungfu_chess.rules.rule_engine import RuleEngine
from kungfu_chess.rules.bishop_rule import BishopRule
from kungfu_chess.rules.king_rule import KingRule
from kungfu_chess.rules.knight_rule import KnightRule
from kungfu_chess.rules.chess_pawn_end_handler import ChessPawnEndHandler
from kungfu_chess.rules.jump_rule import JumpRule
from kungfu_chess.rules.pawn_rule import PawnRule
from kungfu_chess.rules.queen_rule import QueenRule
from kungfu_chess.rules.rook_rule import RookRule
from kungfu_chess.model.piece_kind import PieceKind

ASSETS_ROOT = Path(__file__).resolve().parent.parent.parent / "assets"


class GameFactory:
    """
    Factory responsible for creating and wiring the main game components.

    It assembles the runtime objects required for a game session:
    game state, rule validation, real-time movement handling,
    game engine, input mapping, and controller.

    The factory should only handle object creation and dependency wiring.
    Game rules and gameplay logic belong to their dedicated components.
    """

    CELL_SIZE = 100

    @staticmethod
    def create(board):
        """
        Creates a fully initialized game session.

        Args:
            board: Initial logical board state.

        Returns:
            A tuple containing:
            - Controller responsible for user input handling.
            - GameEngine responsible for game execution.
            - MoveHistoryObserver recording completed moves.
            - ScoreObserver recording capture scores.
        """

        game_state = GameState(board)

        rules = {
            PieceKind.KING: KingRule(),
            PieceKind.QUEEN: QueenRule(),
            PieceKind.ROOK: RookRule(),
            PieceKind.BISHOP: BishopRule(),
            PieceKind.KNIGHT: KnightRule(),
            PieceKind.PAWN: PawnRule(),
        }

        rule_engine = RuleEngine(rules)

        realtime_arbiter = RealTimeArbiter()

        motion_factory = MotionFactory(
            MovementDurationCalculator()
        )

        config_repository = PieceConfigRepository(ASSETS_ROOT)
        state_transition_resolver = StateTransitionResolver(config_repository)
        state_timer = StateTimer()
        collision_resolver = CollisionResolver()
        event_bus = EventBus()
        move_history_observer = MoveHistoryObserver()
        score_observer = ScoreObserver()
        event_bus.subscribe(move_history_observer)
        event_bus.subscribe(score_observer)

        game_engine = GameEngine(
            game_state,
            rule_engine,
            realtime_arbiter,
            motion_factory,
            state_transition_resolver,
            config_repository,
            state_timer,
            collision_resolver,
            ChessPawnEndHandler(),
            JumpRule(),
            event_bus=event_bus,
        )

        board_mapper = BoardMapper(GameFactory.CELL_SIZE)

        controller = Controller(board, board_mapper, game_engine)

        return controller, game_engine, move_history_observer, score_observer