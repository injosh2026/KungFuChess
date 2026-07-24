from dataclasses import dataclass, field

from kungfu_chess.application.game_session import GameSession
from kungfu_chess.server.player_color import PlayerColor
from kungfu_chess.server.player_connection import PlayerConnection


@dataclass
class Match:
    """
    Represents one multiplayer game session.

    A match owns the relation between players
    and one GameSession runtime.
    """

    match_id: str
    game_session: GameSession

    players: dict[str, PlayerConnection] = field(default_factory=dict)

    def add_player(self, player_id: str) -> PlayerColor:

        if len(self.players) >= 2:
            raise ValueError("Match is full")

        color = PlayerColor.WHITE if len(self.players) == 0 else PlayerColor.BLACK

        self.players[player_id] = PlayerConnection(
            player_id=player_id,
            color=color,
            # session=???,
        )

        return color

    def remove_player(self, player_id: str) -> None:
        """
        Removes a player from this match.
        """

        self.players.pop(
            player_id,
            None,
        )

    def receive(
        self,
        player_id: str,
        message,
    ) -> None:
        """
        Receives a message from a connected player.

        Only players belonging to this match may send messages.

        For now the match forwards the message to the game's
        MessageBus. Future versions will validate that the
        player is allowed to perform the requested action.
        """
        if player_id not in self.players:
            raise ValueError("Player is not part of this match")

        self.game_session.message_bus.publish(message)
