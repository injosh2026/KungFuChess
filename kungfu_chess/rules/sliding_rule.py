from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.position import Position


class SlidingRule:

    @staticmethod
    def calculate_destinations(
        board: Board,
        piece: Piece,
        directions: tuple[tuple[int, int], ...]
    ) -> set[Position]:

        destinations = set()

        for row_step, col_step in directions:
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