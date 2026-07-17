from dataclasses import FrozenInstanceError
from types import MappingProxyType

import pytest

from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position
from kungfu_chess.view.game_snapshot import (
    EMPTY_RUNTIME_PROGRESS,
    GameSnapshot,
    PieceSnapshot,
)
from kungfu_chess.view.runtime_role import RuntimeRole


def create_piece_snapshot():
    return PieceSnapshot(
        piece_id=1,
        kind=PieceKind.ROOK,
        color=Color.WHITE,
        position=Position(2,1),
        state=PieceState.IDLE
    )


def test_piece_snapshot_stores_runtime_progress():

    runtime_progress = MappingProxyType({RuntimeRole.RECOVERY: 0.5})
    snapshot = PieceSnapshot(
        piece_id=1,
        kind=PieceKind.ROOK,
        color=Color.WHITE,
        position=Position(2, 1),
        state=PieceState.IDLE,
        runtime_progress=runtime_progress,
    )

    assert snapshot.runtime_progress[RuntimeRole.RECOVERY] == 0.5


def test_piece_snapshot_defaults_to_empty_runtime_progress():
    snapshot = create_piece_snapshot()

    assert snapshot.runtime_progress is EMPTY_RUNTIME_PROGRESS
    assert len(snapshot.runtime_progress) == 0


def test_piece_snapshot_stores_data():

    snapshot = create_piece_snapshot()

    assert snapshot.piece_id == 1
    assert snapshot.kind == PieceKind.ROOK
    assert snapshot.color == Color.WHITE
    assert snapshot.position == Position(2,1)
    assert snapshot.state == PieceState.IDLE


def test_game_snapshot_stores_board_state():

    piece = create_piece_snapshot()

    snapshot = GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=[piece],
        selected_cell=Position(0, 0),
        legal_moves=set(),
        game_over=False,
    )

    assert snapshot.board_width == 8
    assert snapshot.board_height == 8
    assert snapshot.pieces == [piece]
    assert snapshot.selected_cell == Position(0, 0)
    assert snapshot.game_over is False


def test_piece_snapshot_is_read_only():

    snapshot = create_piece_snapshot()

    with pytest.raises(FrozenInstanceError):
        snapshot.position = Position(3, 3)


def test_game_snapshot_is_read_only():

    snapshot = GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=[],
        selected_cell=None,
        legal_moves=set(),
        game_over=False,
    )

    with pytest.raises(FrozenInstanceError):
        snapshot.game_over = True
