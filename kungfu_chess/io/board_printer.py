from kungfu_chess.model.board import Board


class BoardPrinter:

    def print_board(self, board: Board) -> str:

        rows = []

        for row in range(board.height):
            cells = []

            for col in range(board.width):

                piece = board.get_piece_by_position(
                    self._position(row, col)
                )

                if piece is None:
                    cells.append(".")
                else:
                    cells.append(self._piece_to_token(piece))

            rows.append(" ".join(cells))

        return "\n".join(rows)


    def _position(self, row, col):
        from kungfu_chess.model.position import Position

        return Position(row, col)


    def _piece_to_token(self, piece):

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