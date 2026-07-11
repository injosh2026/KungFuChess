from dataclasses import dataclass

from .move_reason import MoveReason


@dataclass(frozen=True)
class MoveValidation:
    is_valid: bool
    reason: MoveReason
