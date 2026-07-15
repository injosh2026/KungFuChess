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


def test_resolve_arrival_returns_no_capture_for_friendly_occupant():
    board = create_board_with_mover_and_optional_occupant(
        occupant_color=Color.WHITE,
    )
    resolver = CollisionResolver()

    outcome = resolver.resolve_arrival(create_motion(), board)

    assert outcome.capture is None
