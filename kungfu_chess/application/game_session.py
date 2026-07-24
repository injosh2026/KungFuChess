from dataclasses import dataclass

from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.events.message_bus import MessageBus
from kungfu_chess.history.move_history_observer import MoveHistoryObserver
from kungfu_chess.input.controller import Controller
from kungfu_chess.scoring.score_observer import ScoreObserver


@dataclass(slots=True)
class GameSession:
    """
    Groups together the runtime objects of one game.

    Higher layers receive a single object instead of several unrelated
    values.
    """

    controller: Controller
    game_engine: GameEngine
    move_history: MoveHistoryObserver
    score: ScoreObserver
    message_bus: MessageBus