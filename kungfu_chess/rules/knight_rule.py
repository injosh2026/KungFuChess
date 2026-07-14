from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.position import Position


class KnightRule:
    """
    Calculates legal destinations for a knight-like piece.

    The knight can move using predefined L-shaped offsets
    and can jump over intermediate pieces.

    This class only calculates possible destinations.
    It does not modify the board or execute movement.
    """

    OFFSETS = (
        (-2, -1),
        (-2, 1),
        (-1, -2),
        (-1, 2),
        (1, -2),
        (1, 2),
        (2, -1),
        (2, 1),
    )

    def legal_destinations(self, board: Board, piece: Piece) -> set[Position]:
        """
        Calculates all legal target positions for the piece.

        A destination is legal when it is inside the board
        and either empty or occupied by an opponent piece.

        Args:
            board: Current game board.
            piece: Piece being evaluated.

        Returns:
            Set of legal destination positions.
        """
        destinations = set()

        for row_offset, col_offset in self.OFFSETS:
            position = Position(
                piece.cell.row + row_offset, piece.cell.col + col_offset
            )

            if not board.is_inside(position):
                continue

            target = board.get_piece_by_position(position)

            if target is None:
                destinations.add(position)

            elif target.color != piece.color:
                destinations.add(position)

        return destinations
