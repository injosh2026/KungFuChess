from abc import ABC, abstractmethod

from kungfu_chess.view.game_snapshot import GameSnapshot


class Renderer(ABC):
    """
    Base interface for game renderers.

    Different renderers can present the same game snapshot
    in different formats such as text or graphical UI.
    """

    @abstractmethod
    def render(self, snapshot: GameSnapshot):
        """
        Renders a game snapshot.

        Args:
            snapshot:
                Immutable representation of the game state.
        """
        pass