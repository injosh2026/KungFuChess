from dataclasses import dataclass, field

from .position import Position
from .piece import Piece


@dataclass
class Board:
    width: int
    height: int
    pieces: dict[Position, Piece] = field(default_factory=dict)

    def is_inside(self, position: Position) -> bool:
        return (
            0 <= position.row < self.height
            and
            0 <= position.col < self.width
        )

    def add_piece(self, piece: Piece) -> None:
        if not self.is_inside(piece.cell):
            raise ValueError("Position outside board")

        if piece.cell in self.pieces:
            raise ValueError("Cell already occupied")

        self.pieces[piece.cell] = piece

    def get_piece(self, position: Position) -> Piece | None:
        return self.pieces.get(position)

    def remove_piece(self, position: Position) -> Piece | None:
        return self.pieces.pop(position, None)

    def move_piece(
        self,
        source: Position,
        target: Position
    ) -> None:

        if target in self.pieces:
            raise ValueError("Target cell occupied")

        piece = self.pieces.pop(source)

        piece.cell = target

        self.pieces[target] = piece