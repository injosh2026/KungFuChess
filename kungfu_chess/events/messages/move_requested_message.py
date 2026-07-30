from dataclasses import dataclass



from kungfu_chess.model.position import Position





@dataclass(frozen=True, slots=True)

class MoveRequestedMessage:

    """

    Request to move a piece from one position to another.



    This message represents an intention to move.

    It does not perform validation and does not modify game state.



    The receiver decides whether the requested move is allowed.

    """



    source: Position

    destination: Position



    def to_wire_format(self) -> str:

        return (

            f"MOVE {self.source.row} {self.source.col} "

            f"{self.destination.row} {self.destination.col}"

        )



    @classmethod

    def from_wire_format(cls, text: str) -> "MoveRequestedMessage":

        parts = text.split()



        if len(parts) != 5 or parts[0] != "MOVE":

            raise ValueError("Invalid MOVE wire format")



        source = Position(int(parts[1]), int(parts[2]))

        destination = Position(int(parts[3]), int(parts[4]))



        return cls(source=source, destination=destination)


