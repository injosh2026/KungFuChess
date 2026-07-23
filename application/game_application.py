from application.game_session import GameSession
from kungfu_chess.engine.game_factory import GameFactory


class GameApplication:
    """
    Application layer responsible for managing game sessions.

    External layers such as servers should communicate
    with this class instead of directly accessing the engine.
    """

    def __init__(self):
        self._sessions: dict[str, GameSession] = {}

    def create_game(self, game_id: str, board) -> GameSession:
        """
        Creates a new game session.
        """

        session = GameFactory.create_session(board)

        self._sessions[game_id] = session

        return session

    def get_game(self, game_id: str) -> GameSession:
        """
        Returns an existing game session.
        """

        return self._sessions[game_id]

    def click(self, game_id: str, x: int, y: int):
        """
        Forwards a click to the requested game session.
        """
        session = self.get_game(game_id)
        return session.controller.handle_click(x, y)

    def wait(self, game_id: str, milliseconds: int):
        """
        Advances simulated time for a game session.
        """
        session = self.get_game(game_id)
        return session.game_engine.wait(milliseconds)


