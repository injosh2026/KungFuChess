from dataclasses import dataclass, field

from .position import Position
from .piece import Piece


@dataclass
class Board:
    width: int
    height: int
    pieces_by_position: dict[Position, Piece] = field(default_factory=dict)
    pieces_by_id: dict[int, Piece] = field(default_factory=dict)

    def is_inside(self, position: Position) -> bool:
        return 0 <= position.row < self.height and 0 <= position.col < self.width

    def add_piece(self, piece: Piece) -> None:
        if not self.is_inside(piece.cell):
            raise ValueError("Position outside board")

        if piece.cell in self.pieces_by_position:
            raise ValueError("Cell already occupied")

        if piece.id in self.pieces_by_id:
            raise ValueError("Piece id already exists")

        self.pieces_by_position[piece.cell] = piece
        self.pieces_by_id[piece.id] = piece

    def get_piece_by_position(self, position: Position) -> Piece | None:
        return self.pieces_by_position.get(position)

    def get_piece_by_id(self, piece_id: int) -> Piece | None:
        return self.pieces_by_id.get(piece_id)

    def remove_piece(self, position: Position) -> Piece | None:
        piece = self.pieces_by_position.pop(position, None)

        if piece is not None:
            self.pieces_by_id.pop(piece.id)

        return piece

    def move_piece(self, source: Position, target: Position) -> Piece | None:
        piece = self.pieces_by_position.pop(source)

        captured_piece = self.remove_piece(target)

        piece.cell = target

        self.pieces_by_position[target] = piece

        return captured_piece
