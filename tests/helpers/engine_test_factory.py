
from pathlib import Path

from kungfu_chess.config.piece_config_repository import PieceConfigRepository
from kungfu_chess.engine.state_transition_resolver import StateTransitionResolver
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.realtime.movement_duration import MovementDurationCalculator
from kungfu_chess.realtime.state_timer import StateTimer
from kungfu_chess.rules.chess_pawn_end_handler import ChessPawnEndHandler
from kungfu_chess.rules.move_validation import MoveValidation
from kungfu_chess.rules.pawn_end_outcome import PendingPawnPromotion
from tests.helpers.config_test_helpers import write_piece_defaults, write_state_config
from tests.helpers.engine_fakes import FakeConfigRepository, FakeMotionFactory, FakeRuleEngine, FakeStateTimer, FakeStateTransitionResolver, FixedJumpDurationResolver, JumpLifecycleTransitionResolver, TrackingMotionFactory, TrackingStateTransitionResolver
from tests.helpers.engine_wiring import build_engine_context
from tests.unit.engine.test_collision_resolver import square


PIECE_CODE = "RW"
LONG_REST_DURATION_MS = 2000
MOTION_DURATION_MS = 1000

def create_engine(validation):

    board = Board(8, 8)

    source_piece = Piece(
        id=1, color=Color.WHITE, kind=PieceKind.ROOK, cell=Position(0, 0)
    )

    board.add_piece(source_piece)

    state = GameState(board)

    rule_engine = FakeRuleEngine(validation)

    context = build_engine_context(
        state,
        rule_engine,
        motion_factory=FakeMotionFactory(),
        config_repository=FakeConfigRepository(),
        state_timer=FakeStateTimer(),
        state_transition_resolver=FakeStateTransitionResolver(),
    )

    return context.engine, state, rule_engine


def create_jump_engine(
    motion_factory=None,
    jump_duration_ms=500,
    state_timer=None,
):
    board = Board(8, 8)

    piece = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.KNIGHT,
        cell=Position(0, 0),
    )

    board.add_piece(piece)

    state = GameState(board)

    rule_engine = FakeRuleEngine(MoveValidation(True, "ok"))

    state_timer = state_timer or FakeStateTimer()

    motion_factory = motion_factory or TrackingMotionFactory()

    context = build_engine_context(
        state,
        rule_engine,
        motion_factory=motion_factory,
        config_repository=FakeConfigRepository(),
        state_timer=state_timer,
        state_transition_resolver=JumpLifecycleTransitionResolver(),
        jump_duration_resolver=FixedJumpDurationResolver(jump_duration_ms),
    )

    return context.engine, state, piece, motion_factory


def create_jump_collision_engine():
    board = Board(8, 8)
    defender = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.KNIGHT,
        cell=Position(0, 3),
    )
    attacker = Piece(
        id=2,
        color=Color.BLACK,
        kind=PieceKind.ROOK,
        cell=Position(0, 0),
    )
    board.add_piece(defender)
    board.add_piece(attacker)
    state = GameState(board)

    context = build_engine_context(
        state,
        FakeRuleEngine(MoveValidation(True, "ok")),
        motion_factory=FakeMotionFactory(),
        config_repository=FakeConfigRepository(),
        state_timer=FakeStateTimer(),
        state_transition_resolver=JumpLifecycleTransitionResolver(),
        jump_duration_resolver=FixedJumpDurationResolver(500),
    )
    return context.engine, state, defender, attacker


def create_motion():

    return Motion(
        piece_id=1, start=Position(0, 0), target=Position(0, 1), duration_ms=1000
    )



def create_configured_engine(
    root: Path,
    move_next_state: str,
    extra_states: tuple[tuple[str, str, float, int | None], ...] = (),
):
    write_piece_defaults(root)
    write_state_config(root, PIECE_CODE, "idle", "idle", speed=0.0)
    write_state_config(root, PIECE_CODE, "move", move_next_state)
    write_state_config(
        root,
        PIECE_CODE,
        "jump",
        "short_rest",
        speed=3.0,
        duration_ms=500,
    )
    for state_name, next_state, speed, duration_ms in extra_states:
        write_state_config(
            root,
            PIECE_CODE,
            state_name,
            next_state,
            speed=speed,
            duration_ms=duration_ms,
        )

    board = Board(8, 8)
    piece = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0),
    )
    board.add_piece(piece)
    state = GameState(board)

    repository = PieceConfigRepository(root)
    resolver = StateTransitionResolver(repository)

    context = build_engine_context(
        state,
        FakeRuleEngine(MoveValidation(True, "ok")),
        motion_factory=FakeMotionFactory(),
        config_repository=repository,
        state_timer=StateTimer(),
        state_transition_resolver=resolver,
        assets_root=root,
    )
    return context.engine, piece


def _build_basic_engine(state, validation=None):
    rule_engine = FakeRuleEngine(
        validation if validation is not None else MoveValidation(True, "ok")
    )
    return build_engine_context(
        state,
        rule_engine,
        motion_factory=FakeMotionFactory(),
        config_repository=FakeConfigRepository(),
        state_timer=FakeStateTimer(),
        state_transition_resolver=FakeStateTransitionResolver(),
    )


def create_crossing_engine():
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
    state = GameState(board)

    context = _build_basic_engine(state)
    return context.engine, state, rook, queen


CELL_MS = MovementDurationCalculator.MOVE_DURATION_PER_CELL_MS


def create_chase_engine(pursuer_id=1, escaper_id=2):
    board = Board(8, 8)
    pursuer = Piece(
        id=pursuer_id,
        color=Color.WHITE,
        kind=PieceKind.QUEEN,
        cell=square("a1"),
    )
    escaper = Piece(
        id=escaper_id,
        color=Color.BLACK,
        kind=PieceKind.PAWN,
        cell=square("a4"),
    )
    board.add_piece(pursuer)
    board.add_piece(escaper)
    state = GameState(board)

    context = _build_basic_engine(state)
    return context.engine, state, pursuer, escaper


def create_friendly_convergence_engine():
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
        cell=Position(0, 5),
    )
    board.add_piece(first)
    board.add_piece(second)
    state = GameState(board)

    context = _build_basic_engine(state)
    return context.engine, state, first, second


def create_promotion_engine(state, pawn, handler, state_transition_resolver=None):
    return build_engine_context(
        state,
        FakeRuleEngine(MoveValidation(True, "ok")),
        motion_factory=FakeMotionFactory(),
        config_repository=FakeConfigRepository(),
        state_timer=FakeStateTimer(),
        state_transition_resolver=state_transition_resolver
        or FakeStateTransitionResolver(),
        pawn_end_handler=handler,
    )


def land_white_pawn_on_promotion_rank(state_transition_resolver=None):
    board = Board(8, 8)
    pawn = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.PAWN,
        cell=Position(1, 3),
    )
    board.add_piece(pawn)
    state = GameState(board)
    transition_resolver = state_transition_resolver or TrackingStateTransitionResolver()
    context = create_promotion_engine(
        state,
        pawn,
        ChessPawnEndHandler(),
        transition_resolver,
    )
    context.engine.realtime_arbiter.start_motion(
        Motion(1, Position(1, 3), Position(0, 3), duration_ms=1000)
    )
    context.engine.wait(1000)
    return context.engine, state, pawn, transition_resolver


def board_with_pending_promotion():
    board = Board(8, 8)
    pawn = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.PAWN,
        cell=Position(0, 3),
    )
    rook = Piece(
        id=2,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(4, 4),
    )
    board.add_piece(pawn)
    board.add_piece(rook)
    state = GameState(board)
    state.pending_pawn_promotion = PendingPawnPromotion(
        piece_id=pawn.id,
        allowed_kinds=ChessPawnEndHandler.PROMOTION_KINDS,
    )
    context = create_promotion_engine(state, pawn, ChessPawnEndHandler())
    return context.engine, state, pawn, rook
