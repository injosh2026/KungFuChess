from pathlib import Path

from kungfu_chess.application.game_session import GameSession
from kungfu_chess.engine.arrival_resolver import ArrivalResolver
from kungfu_chess.engine.jump_duration_resolver import JumpDurationResolver
from kungfu_chess.engine.jump_window_tracker import JumpWindowTracker
from kungfu_chess.engine.services.capture_service import CaptureService
from kungfu_chess.engine.services.jump_service import JumpService
from kungfu_chess.engine.services.motion_completion_service import MotionCompletionService
from kungfu_chess.engine.services.move_service import MoveService
from kungfu_chess.engine.services.pawn_promotion_service import PawnPromotionService
from kungfu_chess.engine.services.simulation_service import SimulationService
from kungfu_chess.engine.services.state_transition_service import StateTransitionService
from kungfu_chess.engine.services.timed_state_service import TimedStateService
from kungfu_chess.events.handlers.jump_request_handler import JumpRequestHandler
from kungfu_chess.events.handlers.move_request_handler import MoveRequestHandler
from kungfu_chess.events.handlers.promotion_request_handler import PromotionRequestHandler
from kungfu_chess.events.message_bus import MessageBus
from kungfu_chess.config.piece_config_repository import PieceConfigRepository
from kungfu_chess.engine.collision_resolver import CollisionResolver
from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.engine.motion_factory import MotionFactory
from kungfu_chess.engine.state_transition_resolver import StateTransitionResolver
from kungfu_chess.events.messages.jump_requested_message import JumpRequestedMessage
from kungfu_chess.events.messages.move_requested_message import MoveRequestedMessage
from kungfu_chess.events.messages.promotion_requested_message import PromotionRequestedMessage
from kungfu_chess.events.move_performed_event import MovePerformedEvent
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

        motion_factory = MotionFactory(MovementDurationCalculator())

        config_repository = PieceConfigRepository(ASSETS_ROOT)
        state_transition_resolver = StateTransitionResolver(config_repository)
        state_timer = StateTimer()
        state_transition_service = StateTransitionService(
            config_repository,
            state_transition_resolver,
            state_timer,
        )
        collision_resolver = CollisionResolver()
        arrival_resolver = ArrivalResolver(game_state)
        jump_window_tracker = JumpWindowTracker()
        capture_service = CaptureService(
            game_state,
            realtime_arbiter,
            jump_window_tracker,
        )
        jump_duration_resolver = JumpDurationResolver(config_repository)
        message_bus = MessageBus()
        move_history_observer = MoveHistoryObserver()
        score_observer = ScoreObserver()
        message_bus.subscribe(
            MovePerformedEvent,
            move_history_observer.handle,
        )
        message_bus.subscribe(MovePerformedEvent, score_observer.handle)

        timed_state_service = TimedStateService(
            game_state,
            state_timer,
            jump_window_tracker,
            config_repository,
            state_transition_service,
        )

        pawn_end_handler = ChessPawnEndHandler()

        pawn_promotion_service = PawnPromotionService(
            game_state,
            pawn_end_handler,
            state_transition_service,
        )

        motion_completion_service = MotionCompletionService(
            game_state,
            realtime_arbiter,
            collision_resolver,
            arrival_resolver,
            capture_service,
            jump_window_tracker,
            state_transition_service,
            pawn_promotion_service,
            message_bus,
        )

        move_service = MoveService(
            game_state,
            rule_engine,
            realtime_arbiter,
            motion_factory,
            config_repository,
        )

        jump_service = JumpService(
            game_state,
            realtime_arbiter,
            state_timer,
            JumpRule(),
            jump_window_tracker,
            jump_duration_resolver,
            config_repository,
        )

        simulation_service = SimulationService(
            game_state,
            realtime_arbiter,
            collision_resolver,
            capture_service,
            motion_completion_service,
            timed_state_service,
            jump_window_tracker,
        )

        game_engine = GameEngine(
            game_state,
            rule_engine,
            realtime_arbiter,
            state_timer,
            move_service,
            jump_service,
            simulation_service,
        )

        move_request_handler = MoveRequestHandler(game_engine)
        jump_request_handler = JumpRequestHandler(game_engine)
        promotion_request_handler = PromotionRequestHandler(game_engine)

        message_bus.subscribe(
            MoveRequestedMessage,
            move_request_handler.handle,
        )

        message_bus.subscribe(
            JumpRequestedMessage,
            jump_request_handler.handle,
        )

        message_bus.subscribe(
            PromotionRequestedMessage,
            promotion_request_handler.handle,
        )

        board_mapper = BoardMapper(GameFactory.CELL_SIZE)

        controller = Controller(board, board_mapper, game_engine, message_bus)

        return controller, game_engine, move_history_observer, score_observer, message_bus

    @staticmethod
    def create_session(board):
        """
        Creates a complete game session object.
        """
        (
            controller,
            game_engine,
            move_history,
            score,
            message_bus
        ) = GameFactory.create(board)

        return GameSession(
            controller=controller,
            game_engine=game_engine,
            move_history=move_history,
            score=score,
            message_bus=message_bus,
        )
