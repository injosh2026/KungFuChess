from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position
from kungfu_chess.view.game_snapshot import (
    GameSnapshot,
    PieceSnapshot,
)
from kungfu_chess.view.text_renderer import TextRenderer


def create_piece_snapshot(
    piece_id,
    color,
    kind,
    x,
    y
):
    return PieceSnapshot(
        piece_id=piece_id,
        color=color,
        kind=kind,
        pixel_position=(x, y),
        state=PieceState.IDLE
    )


def create_snapshot(pieces, game_over=False):

    return GameSnapshot(
        board_width=3,
        board_height=3,
        pieces=pieces,
        selected_cell=None,
        game_over=game_over
    )


def test_renderer_draws_piece_in_correct_position():

    snapshot = create_snapshot(
        [
            create_piece_snapshot(
                1,
                Color.WHITE,
                PieceKind.ROOK,
                100,
                200
            )
        ]
    )

    renderer = TextRenderer()

    result = renderer.render(snapshot)

    expected = (
        ". . .\n"
        ". . .\n"
        ". wR ."
    )

    assert result == expected


def test_renderer_draws_multiple_pieces():

    snapshot = create_snapshot(
        [
            create_piece_snapshot(
                1,
                Color.WHITE,
                PieceKind.KING,
                0,
                0
            ),
            create_piece_snapshot(
                2,
                Color.BLACK,
                PieceKind.QUEEN,
                200,
                100
            )
        ]
    )

    renderer = TextRenderer()

    result = renderer.render(snapshot)

    expected = (
        "wK . .\n"
        ". . bQ\n"
        ". . ."
    )

    assert result == expected


def test_renderer_displays_game_over():

    snapshot = create_snapshot(
        [],
        game_over=True
    )

    renderer = TextRenderer()

    result = renderer.render(snapshot)

    assert result.endswith("GAME OVER")