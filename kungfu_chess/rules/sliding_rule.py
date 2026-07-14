from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.position import Position


class SlidingRule:
    """
    Calculates movement destinations for pieces that move
    continuously in given directions.

    Used by sliding pieces such as rook, bishop, and queen.

    This class only calculates legal destinations on the board.
    It does not perform moves or handle real-time collisions.
    """

    @staticmethod
    def calculate_destinations(
        board: Board, piece: Piece, directions: tuple[tuple[int, int], ...]
    ) -> set[Position]:
        """
        Calculates all reachable positions for a sliding piece.

        Movement continues in each given direction until:
        - The board boundary is reached.
        - A friendly piece blocks the path.
        - An enemy piece is reached and can be captured.

        Args:
            board: Current board state.
            piece: Piece whose destinations are calculated.
            directions: Movement vectors.

        Returns:
            Set of reachable positions.
        """
        destinations = set()

        for row_step, col_step in directions:
            row = piece.cell.row + row_step
            col = piece.cell.col + col_step

            while True:
                position = Position(row, col)

                if not board.is_inside(position):
                    break

                target = board.get_piece_by_position(position)

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
