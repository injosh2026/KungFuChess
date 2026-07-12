from dataclasses import FrozenInstanceError

import pytest

from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position
from kungfu_chess.view.game_snapshot import (
    GameSnapshot,
    PieceSnapshot,
)


def create_piece_snapshot():
    return PieceSnapshot(
        piece_id=1,
        kind=PieceKind.ROOK,
        color=Color.WHITE,
        pixel_position=(100, 200),
        state=PieceState.IDLE
    )


def test_piece_snapshot_stores_data():

    snapshot = create_piece_snapshot()

    assert snapshot.piece_id == 1
    assert snapshot.kind == PieceKind.ROOK
    assert snapshot.color == Color.WHITE
    assert snapshot.pixel_position == (100, 200)
    assert snapshot.state == PieceState.IDLE


def test_game_snapshot_stores_board_state():

    piece = create_piece_snapshot()

    snapshot = GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=[piece],
        selected_cell=Position(0, 0),
        game_over=False
    )

    assert snapshot.board_width == 8
    assert snapshot.board_height == 8
    assert snapshot.pieces == [piece]
    assert snapshot.selected_cell == Position(0, 0)
    assert snapshot.game_over is False


def test_piece_snapshot_is_read_only():

    snapshot = create_piece_snapshot()

    with pytest.raises(FrozenInstanceError):
        snapshot.pixel_position = (300, 300)


def test_game_snapshot_is_read_only():

    snapshot = GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=[],
        selected_cell=None,
        game_over=False
    )

    with pytest.raises(FrozenInstanceError):
        snapshot.game_over = True