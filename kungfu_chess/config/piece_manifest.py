from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PieceManifest:
    initial_state: str
    move_command_state: str
    jump_command_state: str
