from dataclasses import dataclass


@dataclass(frozen=True)
class JumpRequestedMessage:
    piece_id: int