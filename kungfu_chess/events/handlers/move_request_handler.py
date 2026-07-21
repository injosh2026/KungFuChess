from kungfu_chess.events.messages.move_requested_message import (
    MoveRequestedMessage,
)
from kungfu_chess.engine.game_engine import GameEngine


class MoveRequestHandler:
    """
    Handles move request messages.

    Receives movement intentions from MessageBus
    and delegates execution to GameEngine.

    The handler does not validate moves itself.
    The GameEngine remains responsible for game rules.
    """

    def __init__(self, game_engine: GameEngine):
        self._game_engine = game_engine

    def handle(self, message: MoveRequestedMessage):
        """
        Processes a move request.

        Args:
            message:
                Requested movement information.

        Returns:
            Result returned by GameEngine.
        """

        return self._game_engine.request_move(
            message.source,
            message.destination,
        )