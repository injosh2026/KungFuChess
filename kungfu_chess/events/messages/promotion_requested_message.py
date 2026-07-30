from dataclasses import dataclass

from kungfu_chess.model.piece_kind import PieceKind


@dataclass(frozen=True)
class PromotionRequestedMessage:
    """
    Represents a request to promote a pawn.

    Contains only the data required to perform
    the promotion operation.
    """

    piece_id: int
    chosen_kind: PieceKind

    def to_wire_format(self) -> str:
        return f"PROMOTION {self.piece_id} {self.chosen_kind.name}"

    @classmethod
    def from_wire_format(cls, text: str) -> "PromotionRequestedMessage":
        parts = text.split()

        if len(parts) != 3 or parts[0] != "PROMOTION":
            raise ValueError("Invalid PROMOTION wire format")

        try:
            chosen_kind = PieceKind[parts[2]]
        except KeyError as error:
            raise ValueError("Invalid PROMOTION wire format") from error

        return cls(
            piece_id=int(parts[1]),
            chosen_kind=chosen_kind,
        )
