from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Position:
    """
    Represents an immutable position on the logical game board.

    The position stores board coordinates only and contains no game logic,
    movement rules, or rendering information.
    """

    row: int
    col: int
