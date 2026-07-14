from kungfu_chess.io.board_parser import BoardParser
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.position import Position


def test_parses_board_dimensions():

    parser = BoardParser()

    board = parser.parse([
        "wK . .",
        ". wR .",
        ". . bK",
    ])

    assert board.width == 3
    assert board.height == 3


def test_creates_pieces_from_tokens():

    parser = BoardParser()

    board = parser.parse([
        "wK .",
        ". bR",
    ])

    white_king = board.get_piece_by_position(
        Position(0, 0)
    )

    black_rook = board.get_piece_by_position(
        Position(1, 1)
    )

    assert white_king is not None
    assert white_king.color == Color.WHITE
    assert white_king.kind == PieceKind.KING

    assert black_rook is not None
    assert black_rook.color == Color.BLACK
    assert black_rook.kind == PieceKind.ROOK


def test_empty_cells_are_not_pieces():

    parser = BoardParser()

    board = parser.parse([
        "wK .",
        ". .",
    ])

    assert board.get_piece_by_position(
        Position(0, 1)
    ) is None

    assert len(board.pieces_by_id) == 1


def test_assigns_unique_piece_ids():

    parser = BoardParser()

    board = parser.parse([
        "wK bK",
        "wR bR",
    ])

    ids = list(board.pieces_by_id.keys())

    assert len(ids) == 4
    assert len(set(ids)) == 4


def test_rejects_inconsistent_row_width():

    parser = BoardParser()

    try:
        parser.parse([
            "wK .",
            ".",
        ])
        assert False

    except ValueError as error:
        assert str(error) == "Inconsistent row width"


def test_rejects_invalid_piece_token():

    parser = BoardParser()

    try:
        parser.parse([
            "wX",
        ])
        assert False

    except ValueError as error:
        assert str(error) == "Invalid piece token"


def test_rejects_token_with_invalid_length():

    parser = BoardParser()

    try:
        parser.parse([
            "w",
        ])
        assert False

    except ValueError as error:
        assert str(error) == "Invalid piece token"