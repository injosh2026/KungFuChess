from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.view.snapshot_builder import SnapshotBuilder


def create_game_state():

    board = Board(8, 8)

    piece = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(2, 3)
    )

    board.add_piece(piece)

    return GameState(board)


def test_builder_creates_snapshot_from_game_state():

    state = create_game_state()

    builder = SnapshotBuilder()

    snapshot = builder.build(state)

    assert snapshot.board_width == 8
    assert snapshot.board_height == 8
    assert len(snapshot.pieces) == 1


def test_builder_converts_board_position_to_pixel_position():

    state = create_game_state()

    builder = SnapshotBuilder()

    snapshot = builder.build(state)

    piece = snapshot.pieces[0]

    assert piece.pixel_position == (300, 200)


def test_builder_preserves_piece_information():

    state = create_game_state()

    builder = SnapshotBuilder()

    snapshot = builder.build(state)

    piece = snapshot.pieces[0]

    assert piece.piece_id == 1
    assert piece.kind == PieceKind.ROOK
    assert piece.color == Color.WHITE
    assert piece.state == PieceState.IDLE


def test_snapshot_contains_game_over_state():

    state = create_game_state()

    state.game_over = True

    builder = SnapshotBuilder()

    snapshot = builder.build(state)

    assert snapshot.game_over is True


def test_snapshot_uses_selected_cell():

    state = create_game_state()

    builder = SnapshotBuilder()

    selected = Position(2, 3)

    snapshot = builder.build(
        state,
        selected_cell=selected
    )

    assert snapshot.selected_cell == selected