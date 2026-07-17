from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class JumpCommand:
    """
    Carries a jump action request from input to the controller.

    This command contains data only. It does not validate the jump
    or modify game state.
    """

    piece_id: int
