from types import SimpleNamespace

from kungfu_chess.client.client_motion_tracker import ClientMotionTracker
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.snapshot.network_snapshot_source import NetworkSnapshotSource
from kungfu_chess.snapshot.game_snapshot import GameSnapshot, PieceSnapshot
from kungfu_chess.ui.animation_clock import AnimationClock
from kungfu_chess.view.visual_position import VisualPositionCalculator


def test_network_snapshot_source_returns_latest_snapshot():
    source = NetworkSnapshotSource(None)

    snapshot = GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=[],
        selected_cell=None,
        legal_moves=set(),
        game_over=False,
    )

    source.update(snapshot)

    assert source.get_snapshot() == snapshot


def test_network_snapshot_source_returns_none_before_first_update():
    source = NetworkSnapshotSource(None)

    assert source.get_snapshot() is None


def test_network_snapshot_source_overlays_controller_selection():
    controller = SimpleNamespace(
        selected_position=Position(1, 2),
        legal_moves={Position(2, 2), Position(3, 2)},
    )

    source = NetworkSnapshotSource(None, controller=controller)

    server_snapshot = GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=[],
        selected_cell=Position(0, 0),
        legal_moves={Position(0, 1)},
        game_over=False,
    )

    source.update(server_snapshot)

    snapshot = source.get_snapshot()

    assert snapshot.selected_cell == Position(1, 2)
    assert snapshot.legal_moves == {Position(2, 2), Position(3, 2)}
    assert snapshot.board_width == server_snapshot.board_width
    assert snapshot.pieces == server_snapshot.pieces


def test_network_snapshot_source_without_controller_keeps_server_selection():
    source = NetworkSnapshotSource(None)

    server_snapshot = GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=[],
        selected_cell=Position(4, 4),
        legal_moves={Position(5, 4)},
        game_over=False,
    )

    source.update(server_snapshot)

    assert source.get_snapshot() == server_snapshot


def test_network_snapshot_source_does_not_mutate_controller_board():
    board = object()
    controller = SimpleNamespace(
        board=board,
        selected_position=Position(0, 0),
        legal_moves=set(),
    )

    source = NetworkSnapshotSource(None, controller=controller)

    source.update(
        GameSnapshot(
            board_width=8,
            board_height=8,
            pieces=[],
            selected_cell=None,
            legal_moves=set(),
            game_over=False,
        )
    )

    source.get_snapshot()

    assert controller.board is board


def _create_clock(initial_ms=0):
    current_seconds = [initial_ms / 1000.0]
    clock = AnimationClock(time_source=lambda: current_seconds[0])

    def advance(milliseconds):
        current_seconds[0] += milliseconds / 1000.0

    return clock, advance


def _create_authoritative_snapshot():
    return GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=[
            PieceSnapshot(
                piece_id=1,
                kind=PieceKind.ROOK,
                color=Color.WHITE,
                position=Position(0, 0),
                state="idle",
            )
        ],
        selected_cell=None,
        legal_moves=set(),
        game_over=False,
    )


def test_network_snapshot_source_applies_visual_position_during_active_motion():
    clock, advance = _create_clock()
    tracker = ClientMotionTracker()
    calculator = VisualPositionCalculator(100)

    source = NetworkSnapshotSource(
        None,
        motion_tracker=tracker,
        animation_clock=clock,
        visual_position_calculator=calculator,
    )

    authoritative_snapshot = _create_authoritative_snapshot()
    source.update(authoritative_snapshot)

    tracker.start(
        Motion(
            piece_id=1,
            start=Position(0, 0),
            target=Position(0, 3),
            duration_ms=1000,
        ),
        "move",
    )

    source.get_snapshot()
    advance(500)
    render_snapshot = source.get_snapshot()

    render_piece = render_snapshot.pieces[0]

    assert render_piece.visual_position is not None
    assert render_piece.position == Position(0, 0)
    assert source._latest_snapshot.pieces[0].position == Position(0, 0)


def test_network_snapshot_source_applies_motion_state_only_to_render_snapshot():
    clock, _advance = _create_clock()
    tracker = ClientMotionTracker()
    calculator = VisualPositionCalculator(100)

    source = NetworkSnapshotSource(
        None,
        motion_tracker=tracker,
        animation_clock=clock,
        visual_position_calculator=calculator,
    )

    authoritative_snapshot = _create_authoritative_snapshot()
    source.update(authoritative_snapshot)

    tracker.start(
        Motion(
            piece_id=1,
            start=Position(0, 0),
            target=Position(0, 3),
            duration_ms=1000,
            elapsed_ms=500,
        ),
        "move",
    )

    render_snapshot = source.get_snapshot()

    assert source._latest_snapshot.pieces[0].state == "idle"
    assert render_snapshot.pieces[0].state == "move"
    assert render_snapshot.pieces[0].position == Position(0, 0)


def test_network_snapshot_source_reconcile_clears_motion_overlay_on_update():
    clock, _advance = _create_clock()
    tracker = ClientMotionTracker()
    calculator = VisualPositionCalculator(100)

    source = NetworkSnapshotSource(
        None,
        motion_tracker=tracker,
        animation_clock=clock,
        visual_position_calculator=calculator,
    )

    source.update(_create_authoritative_snapshot())

    tracker.start(
        Motion(
            piece_id=1,
            start=Position(0, 0),
            target=Position(0, 3),
            duration_ms=1000,
            elapsed_ms=500,
        ),
        "move",
    )

    source.update(
        GameSnapshot(
            board_width=8,
            board_height=8,
            pieces=[
                PieceSnapshot(
                    piece_id=1,
                    kind=PieceKind.ROOK,
                    color=Color.WHITE,
                    position=Position(0, 3),
                    state="idle",
                )
            ],
            selected_cell=None,
            legal_moves=set(),
            game_over=False,
        )
    )

    render_snapshot = source.get_snapshot()

    assert render_snapshot.pieces[0].visual_position is None
    assert render_snapshot.pieces[0].position == Position(0, 3)
