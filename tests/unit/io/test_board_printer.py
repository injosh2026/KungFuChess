from kungfu_chess.io.board_printer import BoardPrinter
from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position


def create_piece(position, piece_id, color, kind):

    return Piece(
        id=piece_id,
        color=color,
        kind=kind,
        cell=position
    )


def test_prints_empty_board():

    board = Board(3, 2)

    printer = BoardPrinter()

    result = printer.print_board(board)

    assert result == (
        ". . .\n"
        ". . ."
    )


def test_prints_single_piece():

    board = Board(3, 3)

    king = create_piece(
        Position(0, 0),
        1,
        Color.WHITE,
        PieceKind.KING
    )

    board.add_piece(king)

    printer = BoardPrinter()

    result = printer.print_board(board)

    assert result == (
        "wK . .\n"
        ". . .\n"
        ". . ."
    )


def test_prints_multiple_pieces():

    board = Board(3, 3)

    pieces = [
        create_piece(
            Position(0, 0),
            1,
            Color.WHITE,
            PieceKind.KING
        ),
        create_piece(
            Position(1, 1),
            2,
            Color.BLACK,
            PieceKind.ROOK
        ),
        create_piece(
            Position(2, 2),
            3,
            Color.WHITE,
            PieceKind.PAWN
        ),
    ]

    for piece in pieces:
        board.add_piece(piece)


    printer = BoardPrinter()

    result = printer.print_board(board)

    assert result == (
        "wK . .\n"
        ". bR .\n"
        ". . wP"
    )


def test_print_preserves_board_dimensions():

    board = Board(5, 2)

    printer = BoardPrinter()

    result = printer.print_board(board)

    lines = result.split("\n")

    assert len(lines) == 2
    assert len(lines[0].split()) == 5
    assert len(lines[1].split()) == 5