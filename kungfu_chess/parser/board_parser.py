from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position


class BoardParser:

    PIECE_KINDS = {
        "K": PieceKind.KING,
        "Q": PieceKind.QUEEN,
        "R": PieceKind.ROOK,
        "B": PieceKind.BISHOP,
        "N": PieceKind.KNIGHT,
        "P": PieceKind.PAWN,
    }

    COLORS = {
        "w": Color.WHITE,
        "b": Color.BLACK,
    }


    def parse(self, lines: list[str]) -> Board:

        rows = [
            line.split()
            for line in lines
        ]

        height = len(rows)
        width = len(rows[0])

        for row in rows:
            if len(row) != width:
                raise ValueError("Inconsistent row width")


        board = Board(width, height)

        piece_id = 1

        for row_index, row in enumerate(rows):
            for col_index, token in enumerate(row):

                if token == ".":
                    continue

                piece = self._create_piece(
                    token,
                    piece_id,
                    Position(row_index, col_index)
                )

                board.add_piece(piece)

                piece_id += 1

        return board


    def _create_piece(
        self,
        token: str,
        piece_id: int,
        position: Position
    ) -> Piece:

        if len(token) != 2:
            raise ValueError("Invalid piece token")

        color = self.COLORS.get(token[0])
        kind = self.PIECE_KINDS.get(token[1])

        if color is None or kind is None:
            raise ValueError("Invalid piece token")


        return Piece(
            id=piece_id,
            color=color,
            kind=kind,
            cell=position
        )