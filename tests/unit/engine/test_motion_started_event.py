from kungfu_chess.config.state_config import GraphicsConfig, PhysicsConfig, StateConfig
from kungfu_chess.engine.services.move_service import MoveService, PIECE_IN_MOTION
from kungfu_chess.events.message_bus import MessageBus
from kungfu_chess.events.motion_started_event import MotionStartedEvent
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter
from kungfu_chess.rules.move_validation import MoveValidation


class FakeRuleEngine:
    def __init__(self, validation):
        self._validation = validation

    def validate_move(self, board, source, destination):
        return self._validation


class FakeMotionFactory:
    def create(self, piece, source, target):
        return Motion(piece.id, source, target, 1000)


class FakeConfigRepository:
    def get_move_command_state(self, piece_code):
        return "move"


class RejectingRealTimeArbiter(RealTimeArbiter):
    def start_motion(self, motion):
        return False


class RecordingObserver:
    def __init__(self):
        self.events = []

    def handle(self, event) -> None:
        self.events.append(event)


def create_move_service(
    validation,
    *,
    realtime_arbiter=None,
    get_elapsed_ms=lambda: 0,
):
    board = Board(8, 8)
    piece = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0),
    )
    board.add_piece(piece)
    state = GameState(board)

    message_bus = MessageBus()
    observer = RecordingObserver()
    message_bus.subscribe(MotionStartedEvent, observer.handle)

    move_service = MoveService(
        state,
        FakeRuleEngine(validation),
        realtime_arbiter or RealTimeArbiter(),
        FakeMotionFactory(),
        FakeConfigRepository(),
        message_bus,
        get_elapsed_ms,
    )

    return move_service, observer


def test_successful_move_publishes_motion_started_event():
    move_service, observer = create_move_service(MoveValidation(True, "ok"))

    result = move_service.request_move(Position(0, 0), Position(0, 1))

    assert result.is_accepted is True
    assert len(observer.events) == 1

    event = observer.events[0]
    assert isinstance(event, MotionStartedEvent)
    assert event.piece_id == 1
    assert event.start == Position(0, 0)
    assert event.target == Position(0, 1)
    assert event.duration_ms == 1000
    assert event.state == "move"
    assert event.timestamp_ms == 0


def test_successful_move_uses_current_elapsed_ms():
    move_service, observer = create_move_service(
        MoveValidation(True, "ok"),
        get_elapsed_ms=lambda: 750,
    )

    move_service.request_move(Position(0, 0), Position(0, 1))

    assert observer.events[0].timestamp_ms == 750


def test_invalid_move_does_not_publish_motion_started_event():
    move_service, observer = create_move_service(
        MoveValidation(False, "illegal_piece_move")
    )

    result = move_service.request_move(Position(0, 0), Position(3, 3))

    assert result.is_accepted is False
    assert observer.events == []


def test_piece_already_in_motion_does_not_publish_motion_started_event():
    realtime_arbiter = RealTimeArbiter()
    realtime_arbiter.start_motion(
        Motion(1, Position(0, 0), Position(0, 1), 1000)
    )
    move_service, observer = create_move_service(
        MoveValidation(True, "ok"),
        realtime_arbiter=realtime_arbiter,
    )

    result = move_service.request_move(Position(0, 0), Position(0, 1))

    assert result.is_accepted is False
    assert result.reason == PIECE_IN_MOTION
    assert observer.events == []


def test_start_motion_failure_does_not_publish_motion_started_event():
    move_service, observer = create_move_service(
        MoveValidation(True, "ok"),
        realtime_arbiter=RejectingRealTimeArbiter(),
    )

    result = move_service.request_move(Position(0, 0), Position(0, 1))

    assert result.is_accepted is False
    assert result.reason == PIECE_IN_MOTION
    assert observer.events == []
