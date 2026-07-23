from kungfu_chess.engine.services.motion_completion_service import MotionCompletionService
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.realtime.motion_kinematics import CELL_MS
from kungfu_chess.rules.move_validation import MoveValidation
from tests.helpers.engine_test_factory import _build_basic_engine, create_chase_engine, create_crossing_engine, create_engine, create_friendly_convergence_engine
from tests.helpers.engine_wiring import CompleteSimulationService
from tests.unit.engine.test_collision_resolver import square


def test_later_arrival_captures_standing_enemy():
    engine, state, _ = create_engine(MoveValidation(True, "ok"))

    enemy = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.ROOK,
        cell=Position(0, 3),
    )
    state.board.add_piece(enemy)

    engine.request_move(Position(0, 0), Position(0, 3))
    captured = engine.wait(1000)

    assert captured == [enemy]
    assert state.board.get_piece_by_position(Position(0, 3)).id == 1
    assert state.board.get_piece_by_id(2) is None


def test_later_arrival_to_same_cell_captures_earlier_arrival():
    board = Board(8, 8)
    earlier = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0),
    )
    later = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.ROOK,
        cell=Position(2, 0),
    )
    board.add_piece(earlier)
    board.add_piece(later)
    state = GameState(board)

    engine = _build_basic_engine(state).engine

    target = Position(0, 3)
    engine.realtime_arbiter.start_motion(
        Motion(1, Position(0, 0), target, duration_ms=500)
    )
    engine.realtime_arbiter.start_motion(
        Motion(2, Position(2, 0), target, duration_ms=1000)
    )

    captured = engine.wait(1000)

    assert captured == [earlier]
    assert state.board.get_piece_by_position(target).id == 2
    assert state.board.get_piece_by_id(1) is None


def test_same_cell_same_duration_uses_piece_id_tie_break():
    board = Board(8, 8)
    earlier = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0),
    )
    later = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.ROOK,
        cell=Position(2, 0),
    )
    board.add_piece(earlier)
    board.add_piece(later)
    state = GameState(board)

    engine = _build_basic_engine(state).engine

    target = Position(0, 3)
    engine.realtime_arbiter.start_motion(
        Motion(1, Position(0, 0), target, duration_ms=1000)
    )
    engine.realtime_arbiter.start_motion(
        Motion(2, Position(2, 0), target, duration_ms=1000)
    )

    captured = engine.wait(1000)

    assert captured == [earlier]
    assert state.board.get_piece_by_position(target).id == 2
    assert state.board.get_piece_by_id(1) is None


def test_capturing_king_ends_game():

    engine, state, _ = create_engine(MoveValidation(True, "ok"))

    king = Piece(id=2, color=Color.BLACK, kind=PieceKind.KING, cell=Position(0, 1))

    state.board.add_piece(king)

    engine.request_move(Position(0, 0), Position(0, 1))

    captured = engine.wait(1000)

    assert captured == [king]
    assert state.game_over is True


def test_mid_flight_enemy_capture_removes_victim_and_cancels_motion():
    engine, state, rook, queen = create_crossing_engine()

    engine.realtime_arbiter.start_motion(
        Motion(1, square("e1"), square("e8"), duration_ms=7000)
    )
    engine.realtime_arbiter.start_motion(
        Motion(2, square("a4"), square("h4"), duration_ms=7000)
    )

    captured = engine.wait(5000)

    assert captured == [rook]
    assert state.board.get_piece_by_id(1) is None
    assert engine.realtime_arbiter.has_motion(1) is False
    assert engine.realtime_arbiter.has_motion(2) is True


def test_mid_flight_victim_never_reaches_target():
    engine, state, rook, queen = create_crossing_engine()

    engine.realtime_arbiter.start_motion(
        Motion(1, square("e1"), square("e8"), duration_ms=7000)
    )
    engine.realtime_arbiter.start_motion(
        Motion(2, square("a4"), square("h4"), duration_ms=7000)
    )

    engine.wait(5000)
    engine.wait(3000)

    assert state.board.get_piece_by_id(1) is None
    assert state.board.get_piece_by_position(square("e8")) is None
    assert state.board.get_piece_by_id(2) is not None


def test_mid_flight_king_capture_sets_game_over():
    board = Board(8, 8)
    attacker = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("e1"),
    )
    king = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.KING,
        cell=square("d4"),
    )
    board.add_piece(attacker)
    board.add_piece(king)
    state = GameState(board)

    engine = _build_basic_engine(state).engine

    engine.realtime_arbiter.start_motion(
        Motion(1, square("e1"), square("e8"), duration_ms=7000)
    )
    engine.realtime_arbiter.start_motion(
        Motion(2, square("d4"), square("h4"), duration_ms=4000)
    )

    captured = engine.wait(5000)

    assert captured == [king]
    assert state.game_over is True
    assert engine.realtime_arbiter.has_motion(2) is False


def test_standing_enemy_capture_regression_after_event_driven_wait():
    engine, state, _ = create_engine(MoveValidation(True, "ok"))

    enemy = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.ROOK,
        cell=Position(0, 3),
    )
    state.board.add_piece(enemy)

    engine.request_move(Position(0, 0), Position(0, 3))
    captured = engine.wait(1000)

    assert captured == [enemy]
    assert state.board.get_piece_by_position(Position(0, 3)).id == 1
    assert state.board.get_piece_by_id(2) is None


def test_friendly_convergence_keeps_first_piece_at_target():
    engine, state, first, second = create_friendly_convergence_engine()

    target = Position(0, 3)
    engine.realtime_arbiter.start_motion(
        Motion(1, Position(0, 0), target, duration_ms=500)
    )
    engine.realtime_arbiter.start_motion(
        Motion(2, Position(0, 5), target, duration_ms=1000)
    )

    captured = engine.wait(1000)

    assert captured == []
    assert state.board.get_piece_by_id(first.id) is not None
    assert state.board.get_piece_by_position(target).id == first.id
    assert state.board.get_piece_by_id(second.id) is not None
    assert state.board.get_piece_by_position(Position(0, 4)).id == second.id


def test_friendly_arrival_bounce_one_cell():
    board = Board(8, 8)
    mover = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("a1"),
    )
    blocker = Piece(
        id=2,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("a4"),
    )
    board.add_piece(mover)
    board.add_piece(blocker)
    state = GameState(board)

    engine = _build_basic_engine(state).engine

    engine.realtime_arbiter.start_motion(
        Motion(1, square("a1"), square("a4"), duration_ms=3000)
    )

    captured = engine.wait(3000)

    assert captured == []
    assert state.board.get_piece_by_position(square("a3")).id == 1
    assert state.board.get_piece_by_position(square("a4")).id == 2
    assert state.board.get_piece_by_position(square("a1")) is None


def test_friendly_arrival_bounce_skips_friendly_chain():
    board = Board(8, 8)
    mover = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("a1"),
    )
    friendly_four = Piece(
        id=2,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("a4"),
    )
    friendly_five = Piece(
        id=3,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("a5"),
    )
    board.add_piece(mover)
    board.add_piece(friendly_four)
    board.add_piece(friendly_five)
    state = GameState(board)

    engine = _build_basic_engine(state).engine

    engine.realtime_arbiter.start_motion(
        Motion(1, square("a1"), square("a5"), duration_ms=4000)
    )

    captured = engine.wait(4000)

    assert captured == []
    assert state.board.get_piece_by_position(square("a3")).id == 1


def test_friendly_arrival_bounce_captures_enemy_on_path():
    board = Board(8, 8)
    mover = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("a1"),
    )
    enemy = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.ROOK,
        cell=square("a4"),
    )
    friendly = Piece(
        id=3,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=square("a5"),
    )
    board.add_piece(mover)
    board.add_piece(enemy)
    board.add_piece(friendly)
    state = GameState(board)

    engine = _build_basic_engine(state).engine

    engine.realtime_arbiter.start_motion(
        Motion(1, square("a1"), square("a5"), duration_ms=4000)
    )

    captured = engine.wait(4000)

    assert captured == [enemy]
    assert state.board.get_piece_by_position(square("a4")).id == 1
    assert state.board.get_piece_by_id(2) is None


def test_chase_escaping_piece_completes_before_pursuer_arrival():
    engine, state, pursuer, escaper = create_chase_engine()

    engine.realtime_arbiter.start_motion(
        Motion(
            pursuer.id,
            square("a1"),
            square("a4"),
            duration_ms=3 * CELL_MS,
        )
    )
    engine.realtime_arbiter.start_motion(
        Motion(
            escaper.id,
            square("a4"),
            square("a5"),
            duration_ms=CELL_MS,
        )
    )

    captured = engine.wait(3 * CELL_MS)

    assert captured == []
    assert state.board.get_piece_by_id(escaper.id) is not None
    assert state.board.get_piece_by_position(square("a5")).id == escaper.id
    assert state.board.get_piece_by_position(square("a4")).id == pursuer.id


def test_chase_pursuer_captures_when_arriving_before_escape_completes():
    engine, state, pursuer, escaper = create_chase_engine()

    engine.realtime_arbiter.start_motion(
        Motion(
            pursuer.id,
            square("a1"),
            square("a4"),
            duration_ms=3 * CELL_MS,
        )
    )
    engine.wait(2500)
    engine.realtime_arbiter.start_motion(
        Motion(
            escaper.id,
            square("a4"),
            square("a5"),
            duration_ms=CELL_MS,
        )
    )

    captured = engine.wait(500)

    assert captured == [escaper]
    assert state.board.get_piece_by_id(escaper.id) is None
    assert state.board.get_piece_by_position(square("a4")).id == pursuer.id
    assert state.board.get_piece_by_position(square("a5")) is None


def test_chase_same_time_completion_uses_piece_id_priority():
    engine, state, pursuer, escaper = create_chase_engine()

    engine.realtime_arbiter.start_motion(
        Motion(
            pursuer.id,
            square("a1"),
            square("a4"),
            duration_ms=3 * CELL_MS,
        )
    )
    engine.wait(2 * CELL_MS)
    engine.realtime_arbiter.start_motion(
        Motion(
            escaper.id,
            square("a4"),
            square("a5"),
            duration_ms=CELL_MS,
        )
    )

    captured = engine.wait(CELL_MS)

    assert captured == [escaper]
    assert state.board.get_piece_by_id(escaper.id) is None
    assert state.board.get_piece_by_position(square("a4")).id == pursuer.id


def test_occupied_cells_keeps_single_entry_per_piece():
    from kungfu_chess.engine.collision_decisions import STATIONARY_ENTRY_TIME_MS

    occupied_cells = {}
    MotionCompletionService._set_piece_occupied_cell(
        occupied_cells,
        1,
        Color.WHITE,
        Position(0, 0),
        STATIONARY_ENTRY_TIME_MS,
    )
    MotionCompletionService._set_piece_occupied_cell(
        occupied_cells,
        1,
        Color.WHITE,
        Position(0, 1),
        1000,
    )
    MotionCompletionService._set_piece_occupied_cell(
        occupied_cells,
        1,
        Color.WHITE,
        Position(0, 2),
        2000,
    )

    piece_cells = [
        cell for cell, occupant in occupied_cells.items() if occupant.piece_id == 1
    ]

    assert len(piece_cells) == 1
    assert piece_cells[0] == Position(0, 2)


def test_occupied_cells_invariant_during_mid_path_wait():
    from kungfu_chess.engine.collision_decisions import CellEntryEvent

    engine, state, rook, queen = create_crossing_engine()
    simulation_service = engine._simulation_service

    engine.realtime_arbiter.start_motion(
        Motion(1, square("e1"), square("e8"), duration_ms=7000)
    )
    engine.realtime_arbiter.start_motion(
        Motion(2, square("a4"), square("h4"), duration_ms=7000)
    )

    occupied_cells = CompleteSimulationService._build_initial_occupied_cells(
        state.board,
        engine.realtime_arbiter.active_motions(),
    )

    events = simulation_service.collision_resolver.schedule_timeline_events(
        state.board,
        engine.realtime_arbiter.active_motions(),
        within_ms=3500,
    )

    captured_pieces = []
    elapsed = 0
    for event in events:
        step = event.time_from_wait_start_ms - elapsed
        if step > 0:
            engine.realtime_arbiter.advance_time(step)
            elapsed = event.time_from_wait_start_ms

        if isinstance(event, CellEntryEvent):
            outcome = simulation_service.collision_resolver.resolve_entry_event(
                event,
                state.board,
                occupied_cells,
            )
            simulation_service._apply_entry_outcome(
                outcome,
                event,
                occupied_cells,
                captured_pieces,
            )

    for piece_id in (1, 2):
        piece_cells = [
            cell
            for cell, occupant in occupied_cells.items()
            if occupant.piece_id == piece_id
        ]
        assert len(piece_cells) == 1


def test_head_on_same_file_captures_one_enemy():
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
    state = GameState(board)

    engine = _build_basic_engine(state).engine

    engine.realtime_arbiter.start_motion(
        Motion(1, square("e1"), square("e8"), duration_ms=7000)
    )
    engine.realtime_arbiter.start_motion(
        Motion(2, square("e8"), square("e1"), duration_ms=7000)
    )

    captured = engine.wait(5000)

    assert len(captured) == 1
    assert captured[0].id in {1, 2}
    assert state.board.get_piece_by_id(captured[0].id) is None
    assert state.board.get_piece_by_id(3 - captured[0].id) is not None