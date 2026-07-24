from kungfu_chess.server.server_session import ServerSession
from kungfu_chess.server.match import Match
from kungfu_chess.application.game_session import GameSession


class GameServer:

    def __init__(self):
        self.matches: dict[str, Match] = {}
        self.sessions: dict[str, ServerSession] = {}

    def create_match(
        self,
        match_id: str,
        game_session,
    ) -> Match:
        """
        Creates a new multiplayer match.
        """

        match = Match(
            match_id=match_id,
            game_session=game_session,
        )

        self.matches[match_id] = match

        return match

    def join_match(
        self,
        match_id: str,
        player_id: str,
        connection,
    ) -> ServerSession:
        """
        Adds a player to an existing match.
        """

        match = self.matches[match_id]

        color = match.add_player(player_id)

        session = ServerSession(
            match=match,
            game_session=match.game_session,
            player_id=player_id,
            color=color,
            connection=connection,
        )

        self.sessions[player_id] = session

        return session

    def disconnect(
        self,
        player_id: str,
    ) -> None:

        self.sessions.pop(
            player_id,
            None,
        )
