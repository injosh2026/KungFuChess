from dataclasses import dataclass

from .move_reason import MoveReason


@dataclass(frozen=True, slots=True)
class MoveValidation:
    """
    Represents the result of validating a movement request.

    Contains whether the move is accepted and the reason
    explaining the validation result.
    """

    is_valid: bool
    reason: MoveReason
