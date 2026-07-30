from dataclasses import dataclass


@dataclass(frozen=True)
class JumpRequestedMessage:
    piece_id: int



    def to_wire_format(self) -> str:

        return f"JUMP {self.piece_id}"



    @classmethod

    def from_wire_format(cls, text: str) -> "JumpRequestedMessage":

        parts = text.split()



        if len(parts) != 2 or parts[0] != "JUMP":

            raise ValueError("Invalid JUMP wire format")



        return cls(piece_id=int(parts[1]))

