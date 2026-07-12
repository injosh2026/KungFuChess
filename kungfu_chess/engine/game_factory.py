from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.input.board_mapper import BoardMapper
from kungfu_chess.input.controller import Controller
from kungfu_chess.model.game_state import GameState
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter
from kungfu_chess.rules.rule_engine import RuleEngine
from kungfu_chess.rules.bishop_rule import BishopRule
from kungfu_chess.rules.king_rule import KingRule
from kungfu_chess.rules.knight_rule import KnightRule
from kungfu_chess.rules.pawn_rule import PawnRule
from kungfu_chess.rules.queen_rule import QueenRule
from kungfu_chess.rules.rook_rule import RookRule

class GameFactory:

    CELL_SIZE = 100

    @staticmethod
    def create(board):

        game_state = GameState(board)

        rules = [
            KingRule(),
            QueenRule(),
            RookRule(),
            BishopRule(),
            KnightRule(),
            PawnRule(),
        ]

        rule_engine = RuleEngine(rules)

        realtime_arbiter = RealTimeArbiter()

        game_engine = GameEngine(
            game_state,
            rule_engine,
            realtime_arbiter
        )

        board_mapper = BoardMapper(
            GameFactory.CELL_SIZE
        )

        controller = Controller(
            board,
            board_mapper,
            game_engine
        )

        return controller, game_engine