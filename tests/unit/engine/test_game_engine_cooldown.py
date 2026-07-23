
from kungfu_chess.config.piece_config_repository import PieceConfigRepository
from kungfu_chess.engine.services.jump_service import PIECE_IN_COOLDOWN
from kungfu_chess.engine.state_transition_resolver import StateTransitionResolver
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.state_timer import StateTimer
from tests.helpers.config_test_helpers import write_piece_defaults, write_state_config
from tests.helpers.engine_fakes import FakeMotionFactory, FakeRuleEngine
from tests.helpers.engine_wiring import build_engine_context
from tests.helpers.engine_test_factory import LONG_REST_DURATION_MS, MOTION_DURATION_MS, PIECE_CODE, create_configured_engine
from kungfu_chess.rules.move_validation import MoveValidation as MV

def test_request_move_rejects_piece_in_cooldown(tmp_path):
    engine, piece = create_configured_engine(
        tmp_path,
        "long_rest",
        extra_states=(("long_rest", "idle", 0.0, LONG_REST_DURATION_MS),),
    )

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    result = engine.request_move(Position(0, 1), Position(0, 2))

    assert result.is_accepted is False
    assert result.reason == PIECE_IN_COOLDOWN


def test_request_move_allowed_after_cooldown_expires(tmp_path):
    engine, piece = create_configured_engine(
        tmp_path,
        "long_rest",
        extra_states=(("long_rest", "idle", 0.0, LONG_REST_DURATION_MS),),
    )

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(MOTION_DURATION_MS)
    engine.wait(LONG_REST_DURATION_MS)

    result = engine.request_move(Position(0, 1), Position(0, 2))

    assert result.is_accepted is True
    assert result.reason == "ok"


def test_short_rest_without_duration_allows_immediate_next_move(tmp_path):
    engine, piece = create_configured_engine(
        tmp_path,
        "short_rest",
        extra_states=(("short_rest", "idle", 0.0, None),),
    )

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    result = engine.request_move(Position(0, 1), Position(0, 2))

    assert result.is_accepted is True


def test_get_legal_moves_unchanged_during_cooldown(tmp_path):
    from kungfu_chess.rules.rule_engine import RuleEngine
    from kungfu_chess.rules.rook_rule import RookRule
    from kungfu_chess.model.piece_kind import PieceKind as PK

    engine, piece = create_configured_engine(
        tmp_path,
        "long_rest",
        extra_states=(("long_rest", "idle", 0.0, LONG_REST_DURATION_MS),),
    )
    engine.rule_engine = RuleEngine({PK.ROOK: RookRule()})

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    legal_moves = engine.get_legal_moves(Position(0, 1))

    assert Position(0, 2) in legal_moves
    assert engine.is_piece_in_cooldown(piece.id) is True


def test_other_piece_can_move_while_piece_is_in_cooldown(tmp_path):
    write_piece_defaults(tmp_path)
    write_state_config(tmp_path, PIECE_CODE, "idle", "idle", speed=0.0)
    write_state_config(tmp_path, PIECE_CODE, "move", "long_rest")
    write_state_config(
        tmp_path,
        PIECE_CODE,
        "long_rest",
        "idle",
        speed=0.0,
        duration_ms=LONG_REST_DURATION_MS,
    )
    write_state_config(
        tmp_path,
        PIECE_CODE,
        "jump",
        "short_rest",
        speed=3.0,
        duration_ms=500,
    )

    board = Board(8, 8)
    resting_piece = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0),
    )
    free_piece = Piece(
        id=2,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(2, 0),
    )
    board.add_piece(resting_piece)
    board.add_piece(free_piece)
    state = GameState(board)

    repository = PieceConfigRepository(tmp_path)
    resolver = StateTransitionResolver(repository)
    context = build_engine_context(
        state,
        FakeRuleEngine(MV(True, "ok")),
        motion_factory=FakeMotionFactory(),
        config_repository=repository,
        state_timer=StateTimer(),
        state_transition_resolver=resolver,
        assets_root=tmp_path,
    )
    engine = context.engine

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    result = engine.request_move(Position(2, 0), Position(2, 1))

    assert result.is_accepted is True
