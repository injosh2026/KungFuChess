from kungfu_chess.view.game_snapshot import GameSnapshot


class TextRenderer:

    def render(self, snapshot: GameSnapshot) -> str:

        board = [
            ["." for _ in range(snapshot.board_width)]
            for _ in range(snapshot.board_height)
        ]

        for piece in snapshot.pieces:
            row = piece.pixel_position[1] // 100
            col = piece.pixel_position[0] // 100

            board[row][col] = self._piece_symbol(piece)

        lines = [
            " ".join(row)
            for row in board
        ]

        if snapshot.game_over:
            lines.append("GAME OVER")

        return "\n".join(lines)


    def _piece_symbol(self, piece):

        color = {
            "white": "w",
            "black": "b"
        }[piece.color.value]

        kind = {
            "king": "K",
            "queen": "Q",
            "rook": "R",
            "bishop": "B",
            "knight": "N",
            "pawn": "P"
        }[piece.kind.value]

        return color + kind