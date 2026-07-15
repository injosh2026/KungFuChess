from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.realtime.state_timer import StateTimer
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

    assert piece.position == Position(2,3)


def test_builder_preserves_piece_information():

    state = create_game_state()

    builder = SnapshotBuilder()

    snapshot = builder.build(state)

    piece = snapshot.pieces[0]

    assert piece.piece_id == 1
    assert piece.kind == PieceKind.ROOK
    assert piece.color == Color.WHITE
    assert piece.state == PieceState.IDLE
    assert piece.state_progress is None


def test_builder_sets_state_progress_none_without_active_timer():

    state = create_game_state()

    snapshot = SnapshotBuilder().build(state)

    assert snapshot.pieces[0].state_progress is None


def test_builder_reads_state_progress_from_provider():

    state = create_game_state()
    piece = state.board.pieces_by_id[1]
    piece.state = "long_rest"

    timer = StateTimer()
    timer.start(piece.id, 1000)

    builder = SnapshotBuilder(get_state_progress=timer.progress)
    snapshot = builder.build(state)

    assert snapshot.pieces[0].state == "long_rest"
    assert snapshot.pieces[0].state_progress == 0.0


def test_builder_reflects_partial_timer_progress():

    state = create_game_state()
    piece = state.board.pieces_by_id[1]
    piece.state = "long_rest"

    timer = StateTimer()
    timer.start(piece.id, 1000)
    timer.advance(250)

    builder = SnapshotBuilder(get_state_progress=timer.progress)
    snapshot = builder.build(state)

    assert snapshot.pieces[0].state_progress == 0.25


def test_builder_sets_state_progress_none_after_timer_finishes():

    state = create_game_state()
    piece = state.board.pieces_by_id[1]
    piece.state = "idle"

    timer = StateTimer()
    timer.start(piece.id, 1000)
    timer.advance(1000)

    builder = SnapshotBuilder(get_state_progress=timer.progress)
    snapshot = builder.build(state)

    assert snapshot.pieces[0].state == "idle"
    assert snapshot.pieces[0].state_progress is None


def test_state_progress_does_not_affect_visual_position():
    state = create_game_state()
    piece = state.board.pieces_by_id[1]
    piece.state = "long_rest"
    motion = Motion(
        piece_id=1,
        start=Position(2, 3),
        target=Position(4, 3),
        duration_ms=1000,
        elapsed_ms=500,
    )

    timer = StateTimer()
    timer.start(piece.id, 1000)
    timer.advance(250)

    snapshot = SnapshotBuilder(
        get_state_progress=timer.progress,
    ).build(state, motions=(motion,))

    assert snapshot.pieces[0].state == "long_rest"
    assert snapshot.pieces[0].state_progress == 0.25
    assert snapshot.pieces[0].visual_position is not None


def test_builder_uses_piece_state_not_motion():
    state = create_game_state()
    piece = state.board.pieces_by_id[1]
    piece.state = "long_rest"

    snapshot = SnapshotBuilder().build(state)

    assert snapshot.pieces[0].state == "long_rest"


def test_builder_keeps_piece_state_when_motion_is_active():
    state = create_game_state()
    piece = state.board.pieces_by_id[1]
    piece.state = "long_rest"
    motion = Motion(
        piece_id=1,
        start=Position(2, 3),
        target=Position(4, 3),
        duration_ms=1000,
        elapsed_ms=500,
    )

    snapshot = SnapshotBuilder().build(state, motions=(motion,))

    assert snapshot.pieces[0].state == "long_rest"
    assert snapshot.pieces[0].visual_position is not None


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


def test_builder_sets_visual_position_for_multiple_motions():
    board = Board(8, 8)
    first = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0),
    )
    second = Piece(
        id=2,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(2, 0),
    )
    board.add_piece(first)
    board.add_piece(second)
    state = GameState(board)

    motions = (
        Motion(
            piece_id=1,
            start=Position(0, 0),
            target=Position(0, 3),
            duration_ms=1000,
            elapsed_ms=500,
        ),
        Motion(
            piece_id=2,
            start=Position(2, 0),
            target=Position(2, 3),
            duration_ms=1000,
            elapsed_ms=250,
        ),
    )

    snapshot = SnapshotBuilder().build(state, motions=motions)

    visual_by_id = {piece.piece_id: piece.visual_position for piece in snapshot.pieces}

    assert visual_by_id[1] is not None
    assert visual_by_id[2] is not None
    assert visual_by_id[1] != visual_by_id[2]