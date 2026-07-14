from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.engine.motion_factory import MotionFactory
from kungfu_chess.input.board_mapper import BoardMapper
from kungfu_chess.input.controller import Controller
from kungfu_chess.model.game_state import GameState
from kungfu_chess.realtime.movement_duration import MovementDurationCalculator
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter
from kungfu_chess.rules.rule_engine import RuleEngine
from kungfu_chess.rules.bishop_rule import BishopRule
from kungfu_chess.rules.king_rule import KingRule
from kungfu_chess.rules.knight_rule import KnightRule
from kungfu_chess.rules.pawn_rule import PawnRule
from kungfu_chess.rules.queen_rule import QueenRule
from kungfu_chess.rules.rook_rule import RookRule
from kungfu_chess.model.piece_kind import PieceKind


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

        game_engine = GameEngine(game_state, rule_engine, realtime_arbiter, motion_factory)

        board_mapper = BoardMapper(GameFactory.CELL_SIZE)

        controller = Controller(board, board_mapper, game_engine)

        return controller, game_engine