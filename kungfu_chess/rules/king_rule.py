from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.position import Position


class KingRule:

    OFFSETS = (
        (-1, -1),
        (-1, 0),
        (-1, 1),
        (0, -1),
        (0, 1),
        (1, -1),
        (1, 0),
        (1, 1),
    )

    def legal_destinations(
        self,
        board: Board,
        piece: Piece
    ) -> set[Position]:

        destinations = set()

        for row_offset, col_offset in self.OFFSETS:
            position = Position(
                piece.cell.row + row_offset,
                piece.cell.col + col_offset
            )

            if not board.is_inside(position):
                continue

            target = board.get_piece_by_position(position)

            if target is None:
                destinations.add(position)

            elif target.color != piece.color:
                destinations.add(position)

        return destinations