from kungfu_chess.view.game_snapshot import GameSnapshot
from kungfu_chess.view.renderer import Renderer


class TextRenderer(Renderer):
    """
    Renders a game snapshot as a textual board representation.

    This renderer only consumes snapshots and does not access
    mutable game state.
    """

    def render(self, snapshot: GameSnapshot) -> str:
        """
        Converts a game snapshot into a text representation.

        Args:
            snapshot:
                Immutable game state snapshot.

        Returns:
            Board representation as text.
        """
        board = [
            ["." for _ in range(snapshot.board_width)]
            for _ in range(snapshot.board_height)
        ]

        for piece in snapshot.pieces:
            row = piece.position.row
            col = piece.position.col

            board[row][col] = self._piece_symbol(piece)

        lines = [" ".join(row) for row in board]

        if snapshot.game_over:
            lines.append("GAME OVER")

        return "\n".join(lines)

    def _piece_symbol(self, piece):
        """
        Converts a piece snapshot into its text symbol.

        Example:
            White rook -> "wR"
        """
        color = {"white": "w", "black": "b"}[piece.color.value]

        kind = {
            "king": "K",
            "queen": "Q",
            "rook": "R",
            "bishop": "B",
            "knight": "N",
            "pawn": "P",
        }[piece.kind.value]

        return color + kind
