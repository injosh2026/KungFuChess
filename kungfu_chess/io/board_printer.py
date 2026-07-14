from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.position import Position


class BoardPrinter:
    """
    Converts a Board object into a textual representation.

    BoardPrinter is responsible only for presentation.
    It does not modify the board or apply game rules.
    """

    def print_board(self, board: Board) -> str:
        """
        Creates a text representation of the current board.

        Args:
            board:
                Board to convert.

        Returns:
            Text representation where pieces are represented
            by two-character tokens and empty cells by ".".
        """
        rows = []

        for row in range(board.height):
            cells = []

            for col in range(board.width):

                piece = board.get_piece_by_position(self._position(row, col))

                if piece is None:
                    cells.append(".")
                else:
                    cells.append(self._piece_to_token(piece))

            rows.append(" ".join(cells))

        return "\n".join(rows)

    def _position(self, row: int, col: int) -> Position:
        return Position(row, col)

    def _piece_to_token(self, piece: Piece) -> str:
        """
        Converts a Piece object into its text token.

        Example:
            White rook -> "wR"
            Black king -> "bK"
        """
        color = {
            "white": "w",
            "black": "b",
        }[piece.color.value]

        kind = {
            "king": "K",
            "queen": "Q",
            "rook": "R",
            "bishop": "B",
            "knight": "N",
            "pawn": "P",
        }[piece.kind.value]

        return color + kind
