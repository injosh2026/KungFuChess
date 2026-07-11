from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.position import Position


class RookRule:

    DIRECTIONS = (
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
    )

    def legal_destinations(
        self,
        board: Board,
        piece: Piece
    ) -> set[Position]:

        destinations = set()

        for row_step, col_step in self.DIRECTIONS:
            row = piece.cell.row + row_step
            col = piece.cell.col + col_step

            while board.is_inside(Position(row, col)):
                position = Position(row, col)
                target = board.get_piece(position)

                if target is None:
                    destinations.add(position)

                elif target.color != piece.color:
                    destinations.add(position)
                    break

                else:
                    break

                row += row_step
                col += col_step

        return destinations