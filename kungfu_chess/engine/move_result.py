from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MoveResult:
    """
    Represents the outcome of a move request.

    MoveResult is returned by GameEngine after validating
    a requested action.

    It contains only the result status and reason.
    It does not perform validation or modify game state.
    """
    is_accepted: bool
    reason: str
