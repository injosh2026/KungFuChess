from kungfu_chess.engine.collision_resolver import CollisionResolver
from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion

TARGET = Position(0, 3)


def create_board_with_mover_and_optional_occupant(
    occupant_color=None,
):
    board = Board(8, 8)
    mover = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0),
    )
    board.add_piece(mover)

    if occupant_color is not None:
        occupant = Piece(
            id=2,
            color=occupant_color,
            kind=PieceKind.ROOK,
            cell=TARGET,
        )
        board.add_piece(occupant)

    return board


def create_motion(piece_id=1, duration_ms=1000):
    return Motion(
        piece_id=piece_id,
        start=Position(0, 0),
        target=TARGET,
        duration_ms=duration_ms,
    )


def test_sort_arrivals_orders_by_duration_then_piece_id():
    resolver = CollisionResolver()

    first = create_motion(piece_id=3, duration_ms=1000)
    second = create_motion(piece_id=1, duration_ms=500)
    third = create_motion(piece_id=2, duration_ms=500)

    sorted_motions = resolver.sort_arrivals([first, second, third])

    assert sorted_motions == (second, third, first)


def test_resolve_arrival_returns_no_capture_for_empty_target():
    board = create_board_with_mover_and_optional_occupant()
    resolver = CollisionResolver()

    outcome = resolver.resolve_arrival(create_motion(), board)

    assert outcome.capture is None


def test_resolve_arrival_returns_capture_for_enemy_occupant():
    board = create_board_with_mover_and_optional_occupant(
        occupant_color=Color.BLACK,
    )
    resolver = CollisionResolver()

    outcome = resolver.resolve_arrival(create_motion(), board)

    assert outcome.capture is not None
    assert outcome.capture.capturer_piece_id == 1
    assert outcome.capture.victim_piece_id == 2
    assert outcome.capture.at_cell == TARGET


def test_resolve_arrival_returns_bounce_cell_for_friendly_occupant():
    board = create_board_with_mover_and_optional_occupant(
        occupant_color=Color.WHITE,
    )
    resolver = CollisionResolver()

    outcome = resolver.resolve_arrival(create_motion(), board)

    assert outcome.capture is None
    assert outcome.arrival_cell == Position(0, 2)


def test_resolve_arrival_returns_bounce_cell_for_friendly_chain():
    board = Board(8, 8)
    mover = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0),
    )
    friendly_at_four = Piece(
        id=2,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 4),
    )
    friendly_at_five = Piece(
        id=3,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 5),
    )
    board.add_piece(mover)
    board.add_piece(friendly_at_four)
    board.add_piece(friendly_at_five)

    motion = Motion(
        piece_id=1,
        start=Position(0, 0),
        target=Position(0, 5),
        duration_ms=5000,
    )
    resolver = CollisionResolver()

    outcome = resolver.resolve_arrival(motion, board)

    assert outcome.capture is None
    assert outcome.arrival_cell == Position(0, 3)


def test_resolve_arrival_returns_capture_on_bounce_path_enemy():
    board = Board(8, 8)
    mover = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0),
    )
    enemy = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.ROOK,
        cell=Position(0, 4),
    )
    friendly = Piece(
        id=3,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 5),
    )
    board.add_piece(mover)
    board.add_piece(enemy)
    board.add_piece(friendly)

    motion = Motion(
        piece_id=1,
        start=Position(0, 0),
        target=Position(0, 5),
        duration_ms=5000,
    )
    resolver = CollisionResolver()

    outcome = resolver.resolve_arrival(motion, board)

    assert outcome.capture is not None
    assert outcome.capture.victim_piece_id == 2
    assert outcome.capture.at_cell == Position(0, 4)
    assert outcome.arrival_cell == Position(0, 4)


def square(name: str) -> Position:
    file_index = ord(name[0]) - ord("a")
    rank_index = int(name[1]) - 1
    return Position(rank_index, file_index)


def test_schedule_timeline_events_returns_mid_path_entry_and_completion():
    from kungfu_chess.engine.collision_decisions import (
        CellEntryEvent,
        MotionCompletionEvent,
    )

    board = Board(8, 8)
    rook = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("e1"),
    )
    board.add_piece(rook)

    motion = Motion(
        piece_id=1,
        start=square("e1"),
        target=square("e8"),
        duration_ms=7000,
    )
    resolver = CollisionResolver()

    events = resolver.schedule_timeline_events(
        board,
        (motion,),
        within_ms=8000,
    )

    assert any(isinstance(event, CellEntryEvent) for event in events)
    assert any(isinstance(event, MotionCompletionEvent) for event in events)


def test_schedule_timeline_events_orders_entry_before_completion_at_same_time():
    from kungfu_chess.engine.collision_decisions import (
        CellEntryEvent,
        MotionCompletionEvent,
    )

    board = Board(8, 8)
    rook = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("e1"),
    )
    finisher = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.ROOK,
        cell=square("a1"),
    )
    board.add_piece(rook)
    board.add_piece(finisher)

    entry_motion = Motion(
        piece_id=1,
        start=square("e1"),
        target=square("e8"),
        duration_ms=7000,
        elapsed_ms=500,
    )
    completion_motion = Motion(
        piece_id=2,
        start=square("a1"),
        target=square("a2"),
        duration_ms=500,
    )
    resolver = CollisionResolver()

    events = resolver.schedule_timeline_events(
        board,
        (entry_motion, completion_motion),
        within_ms=8000,
    )

    same_time_events = [
        event for event in events if event.time_from_wait_start_ms == 500
    ]
    assert len(same_time_events) == 2
    assert isinstance(same_time_events[0], CellEntryEvent)
    assert isinstance(same_time_events[1], MotionCompletionEvent)


def test_schedule_timeline_events_has_no_mid_path_events_for_knight():
    from kungfu_chess.engine.collision_decisions import (
        CellEntryEvent,
        MotionCompletionEvent,
    )

    board = Board(8, 8)
    knight = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.KNIGHT,
        cell=square("a1"),
    )
    board.add_piece(knight)

    motion = Motion(
        piece_id=1,
        start=square("a1"),
        target=square("c2"),
        duration_ms=2000,
    )
    resolver = CollisionResolver()

    events = resolver.schedule_timeline_events(
        board,
        (motion,),
        within_ms=3000,
    )

    assert all(not isinstance(event, CellEntryEvent) for event in events)
    assert any(isinstance(event, MotionCompletionEvent) for event in events)


def test_resolve_entry_event_returns_capture_for_enemy_standing_occupant():
    from kungfu_chess.engine.collision_decisions import (
        CellEntryEvent,
        CellOccupant,
        STATIONARY_ENTRY_TIME_MS,
    )

    board = create_board_with_mover_and_optional_occupant(
        occupant_color=Color.BLACK,
    )
    motion = create_motion()
    event = CellEntryEvent(
        piece_id=1,
        cell=TARGET,
        time_from_wait_start_ms=1000,
        motion=motion,
        path_index=1,
    )
    occupied_cells = {
        TARGET: CellOccupant(
            piece_id=2,
            color=Color.BLACK,
            entry_time_ms=STATIONARY_ENTRY_TIME_MS,
        )
    }
    resolver = CollisionResolver()

    outcome = resolver.resolve_entry_event(event, board, occupied_cells)

    assert outcome.capture is not None
    assert outcome.capture.capturer_piece_id == 1
    assert outcome.capture.victim_piece_id == 2


def test_resolve_entry_event_returns_no_capture_for_empty_cell():
    from kungfu_chess.engine.collision_decisions import CellEntryEvent

    board = create_board_with_mover_and_optional_occupant()
    event = CellEntryEvent(
        piece_id=1,
        cell=TARGET,
        time_from_wait_start_ms=1000,
        motion=create_motion(),
        path_index=1,
    )
    resolver = CollisionResolver()

    outcome = resolver.resolve_entry_event(event, board, {})

    assert outcome.capture is None


def test_resolve_entry_event_returns_no_capture_for_friendly_occupant():
    from kungfu_chess.engine.collision_decisions import (
        CellEntryEvent,
        CellOccupant,
        STATIONARY_ENTRY_TIME_MS,
    )

    board = create_board_with_mover_and_optional_occupant(
        occupant_color=Color.WHITE,
    )
    event = CellEntryEvent(
        piece_id=1,
        cell=TARGET,
        time_from_wait_start_ms=1000,
        motion=create_motion(),
        path_index=1,
    )
    occupied_cells = {
        TARGET: CellOccupant(
            piece_id=2,
            color=Color.WHITE,
            entry_time_ms=STATIONARY_ENTRY_TIME_MS,
        )
    }
    resolver = CollisionResolver()

    outcome = resolver.resolve_entry_event(event, board, occupied_cells)

    assert outcome.capture is None


def test_resolve_entry_event_returns_capture_for_crossing_path_enemy():
    from kungfu_chess.engine.collision_decisions import CellEntryEvent

    board = Board(8, 8)
    rook = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("e1"),
    )
    queen = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.QUEEN,
        cell=square("a4"),
    )
    board.add_piece(rook)
    board.add_piece(queen)

    queen_motion = Motion(
        piece_id=2,
        start=square("a4"),
        target=square("h4"),
        duration_ms=7000,
        elapsed_ms=4000,
    )
    rook_motion = Motion(
        piece_id=1,
        start=square("e1"),
        target=square("e8"),
        duration_ms=7000,
        elapsed_ms=4000,
    )
    event = CellEntryEvent(
        piece_id=2,
        cell=square("e4"),
        time_from_wait_start_ms=4000,
        motion=queen_motion,
        path_index=4,
    )
    resolver = CollisionResolver()

    outcome = resolver.resolve_entry_event(
        event,
        board,
        {},
        active_motions=(queen_motion, rook_motion),
    )

    assert outcome.capture is not None
    assert outcome.capture.capturer_piece_id == 2
    assert outcome.capture.victim_piece_id == 1
    assert outcome.capture.at_cell == square("e4")


def test_resolve_entry_event_returns_capture_for_head_on_enemy():
    from kungfu_chess.engine.collision_decisions import CellEntryEvent

    board = Board(8, 8)
    white_rook = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("e1"),
    )
    black_rook = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.ROOK,
        cell=square("e8"),
    )
    board.add_piece(white_rook)
    board.add_piece(black_rook)

    white_motion = Motion(
        piece_id=1,
        start=square("e1"),
        target=square("e8"),
        duration_ms=7000,
        elapsed_ms=4000,
    )
    black_motion = Motion(
        piece_id=2,
        start=square("e8"),
        target=square("e1"),
        duration_ms=7000,
        elapsed_ms=4000,
    )
    event = CellEntryEvent(
        piece_id=2,
        cell=square("e4"),
        time_from_wait_start_ms=4000,
        motion=black_motion,
        path_index=4,
    )
    resolver = CollisionResolver()

    outcome = resolver.resolve_entry_event(
        event,
        board,
        {},
        active_motions=(white_motion, black_motion),
    )

    assert outcome.capture is not None
    assert outcome.capture.capturer_piece_id == 2
    assert outcome.capture.victim_piece_id == 1
    assert outcome.capture.at_cell == square("e4")


def test_resolve_entry_event_returns_no_capture_for_friendly_path_overlap():
    from kungfu_chess.engine.collision_decisions import CellEntryEvent

    board = Board(8, 8)
    first = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("e1"),
    )
    second = Piece(
        id=2,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("a4"),
    )
    board.add_piece(first)
    board.add_piece(second)

    second_motion = Motion(
        piece_id=2,
        start=square("a4"),
        target=square("h4"),
        duration_ms=7000,
        elapsed_ms=4000,
    )
    first_motion = Motion(
        piece_id=1,
        start=square("e1"),
        target=square("e8"),
        duration_ms=7000,
        elapsed_ms=4000,
    )
    event = CellEntryEvent(
        piece_id=2,
        cell=square("e4"),
        time_from_wait_start_ms=4000,
        motion=second_motion,
        path_index=4,
    )
    resolver = CollisionResolver()

    outcome = resolver.resolve_entry_event(
        event,
        board,
        {},
        active_motions=(second_motion, first_motion),
    )

    assert outcome.capture is None
