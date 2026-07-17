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

    WHITE_STARTING_RANK = 6
    BLACK_STARTING_RANK = 1
    DOUBLE_STEP_CELLS = 2

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
            self._add_first_move_double_step(
                board,
                piece,
                direction,
                destinations,
            )

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

    def _is_on_starting_rank(self, piece: Piece) -> bool:
        if piece.color == Color.WHITE:
            return piece.cell.row == self.WHITE_STARTING_RANK

        return piece.cell.row == self.BLACK_STARTING_RANK

    def _add_first_move_double_step(
        self,
        board: Board,
        piece: Piece,
        direction: int,
        destinations: set[Position],
    ) -> None:
        if piece.has_moved or not self._is_on_starting_rank(piece):
            return

        double_step = Position(
            piece.cell.row + self.DOUBLE_STEP_CELLS * direction,
            piece.cell.col,
        )

        if (
            board.is_inside(double_step)
            and board.get_piece_by_position(double_step) is None
        ):
            destinations.add(double_step)
