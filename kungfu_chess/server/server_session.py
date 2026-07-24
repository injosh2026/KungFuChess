from typing import Any

from kungfu_chess.application.game_session import GameSession
from kungfu_chess.events.move_performed_event import MovePerformedEvent
from kungfu_chess.server.player_color import PlayerColor
from kungfu_chess.server.match import Match


class ServerSession:

    def __init__(
        self,
        match: Match,
        game_session: GameSession,
        player_id: str,
        color: PlayerColor,
        connection=None,
    ):
        self.match = match
        self.game_session = game_session
        self.player_id = player_id
        self.color = color
        self.connection = connection
        self.outbox: list[Any] = []

        self.game_session.message_bus.subscribe(
            MovePerformedEvent,
            self.send,
        )

    def receive(self, message: Any) -> None:
        """
        Receives message from client.

        The message is forwarded to the game communication layer.
        """

        self.match.receive(
            self.player_id,
            message,
        )

    def send(self, message: Any) -> None:
        """
        Stores outgoing messages.

        Later replaced by websocket transport.
        """

        self.outbox.append(message)

        if self.connection is not None:
            self.connection.send(message)
