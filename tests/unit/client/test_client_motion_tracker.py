from kungfu_chess.client.client_motion_tracker import ClientMotionTracker
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.snapshot.game_snapshot import GameSnapshot, PieceSnapshot


def create_snapshot(piece_id=1, position=Position(0, 0)):
    return GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=[
            PieceSnapshot(
                piece_id=piece_id,
                kind=PieceKind.ROOK,
                color=Color.WHITE,
                position=position,
                state="idle",
            )
        ],
        selected_cell=None,
        legal_moves=set(),
        game_over=False,
    )


def test_start_and_advance_updates_elapsed_time():
    tracker = ClientMotionTracker()
    motion = Motion(
        piece_id=1,
        start=Position(0, 0),
        target=Position(0, 3),
        duration_ms=1000,
    )

    tracker.start(motion, "move")
    tracker.advance(250)

    active_motion = tracker.active_motions()[0]

    assert active_motion.elapsed_ms == 250


def test_advance_caps_motion_at_duration():
    tracker = ClientMotionTracker()
    motion = Motion(
        piece_id=1,
        start=Position(0, 0),
        target=Position(0, 3),
        duration_ms=1000,
    )

    tracker.start(motion, "move")
    tracker.advance(750)
    tracker.advance(500)

    active_motion = tracker.active_motions()[0]

    assert active_motion.elapsed_ms == 1000


def test_start_replaces_existing_motion_for_same_piece():
    tracker = ClientMotionTracker()

    tracker.start(
        Motion(1, Position(0, 0), Position(0, 1), 1000),
        "move",
    )
    tracker.start(
        Motion(1, Position(0, 0), Position(0, 2), 800),
        "move",
    )

    active_motions = tracker.active_motions()

    assert len(active_motions) == 1
    assert active_motions[0].target == Position(0, 2)
    assert active_motions[0].duration_ms == 800
    assert tracker.motion_state_for(1) == "move"


def test_reconcile_clears_motion_when_authoritative_position_reaches_target():
    tracker = ClientMotionTracker()
    tracker.start(
        Motion(1, Position(0, 0), Position(0, 3), 1000, elapsed_ms=500),
        "move",
    )

    tracker.reconcile(create_snapshot(position=Position(0, 3)))

    assert tracker.active_motions() == ()
    assert tracker.motion_state_for(1) is None


def test_reconcile_does_not_clear_unrelated_active_motion():
    tracker = ClientMotionTracker()
    tracker.start(
        Motion(1, Position(0, 0), Position(0, 3), 1000, elapsed_ms=250),
        "move",
    )

    snapshot = GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=[
            PieceSnapshot(
                piece_id=1,
                kind=PieceKind.ROOK,
                color=Color.WHITE,
                position=Position(0, 0),
                state="move",
            ),
            PieceSnapshot(
                piece_id=2,
                kind=PieceKind.ROOK,
                color=Color.BLACK,
                position=Position(1, 1),
                state="idle",
            ),
        ],
        selected_cell=None,
        legal_moves=set(),
        game_over=False,
    )

    tracker.reconcile(snapshot)

    assert len(tracker.active_motions()) == 1
    assert tracker.active_motions()[0].piece_id == 1
    assert tracker.motion_state_for(1) == "move"


def test_snapshot_before_motion_started_does_not_start_stale_motion():
    tracker = ClientMotionTracker()

    tracker.reconcile(create_snapshot(position=Position(0, 1)))

    tracker.start(
        Motion(1, Position(0, 0), Position(0, 1), 1000),
        "move",
    )

    assert tracker.active_motions() == ()
    assert tracker.motion_state_for(1) is None
