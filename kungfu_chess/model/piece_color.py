from enum import Enum


class Color(Enum):
    """
    Represents the owner of a game piece.

    Colors are used to distinguish friendly and opposing pieces
    throughout the game logic.
    """

    WHITE = "white"
    BLACK = "black"
