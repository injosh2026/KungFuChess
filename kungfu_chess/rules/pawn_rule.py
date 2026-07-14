from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.position import Position


class PawnRule:
    """
    Defines movement rules for pawn pieces.

    Currently supports forward movement and diagonal captures.
    The movement direction is based on piece color and may later
    be replaced by configurable game rules.
    """

    def legal_destinations(self, board: Board, piece: Piece) -> set[Position]:
        """
        Calculates all legal destination positions for a pawn.

        Args:
            board: Current game board.
            piece: Pawn whose movement is being evaluated.

        Returns:
            Set of positions the pawn can legally move to.
        """
        destinations = set()

        direction = self._direction(piece.color)

        # forward move
        forward = Position(piece.cell.row + direction, piece.cell.col)

        if board.is_inside(forward) and board.get_piece_by_position(forward) is None:
            destinations.add(forward)

        # diagonal captures
        for col_offset in (-1, 1):
            capture_position = Position(
                piece.cell.row + direction, piece.cell.col + col_offset
            )

            if not board.is_inside(capture_position):
                continue

            target = board.get_piece_by_position(capture_position)

            if target is not None and target.color != piece.color:
                destinations.add(capture_position)

        return destinations

    def _direction(self, color: Color) -> int:
        if color == Color.WHITE:
            return -1

        return 1
