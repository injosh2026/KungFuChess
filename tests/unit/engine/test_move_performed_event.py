from kungfu_chess.config.state_config import GraphicsConfig, PhysicsConfig, StateConfig
from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.events.message_bus import MessageBus
from kungfu_chess.events.move_performed_event import MovePerformedEvent
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

    def get_jump_command_state(self, piece_code):
        return "jump"

    def load_state(self, piece_code, state_name):
        return StateConfig(
            physics=PhysicsConfig(
                speed_m_per_sec=0.0,
                next_state_when_finished=state_name,
            ),
            graphics=GraphicsConfig(frames_per_sec=12, is_loop=True),
        )


class FakeStateTransitionResolver:
    def resolve(self, piece_code, current_state):
        return "idle"


class FakeStateTimer:
    def start(self, piece_id, duration_ms):
        pass

    def advance(self, milliseconds, *, only_piece_ids=None):
        return []

    def progress(self, piece_id):
        return None

    def active_piece_ids(self):
        return []

    def has_active_timer(self, piece_id):
        return False


class RecordingObserver:
    def __init__(self):
        self.events = []

    def handle(self, event) -> None:
        self.events.append(event)


def create_engine_with_observer(validation):
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
    message_bus.subscribe(
        MovePerformedEvent,
        observer.handle,
    )

    engine = GameEngine(
        state,
        FakeRuleEngine(validation),
        RealTimeArbiter(),
        FakeMotionFactory(),
        FakeStateTransitionResolver(),
        FakeConfigRepository(),
        FakeStateTimer(),
        message_bus=message_bus,
    )
    return engine, state, observer


def test_move_completion_publishes_move_performed_event():
    engine, state, observer = create_engine_with_observer(
        MoveValidation(True, "ok")
    )

    engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(1000)

    assert len(observer.events) == 1
    event = observer.events[0]
    assert isinstance(event, MovePerformedEvent)
    assert event.piece_id == 1
    assert event.piece_code == "RW"
    assert event.piece_name == "rook"
    assert event.from_position == Position(0, 0)
    assert event.to_position == Position(0, 1)
    assert event.timestamp_ms == 1000
    assert event.capture is None
    assert event.jump_used is False
    assert state.board.get_piece_by_position(Position(0, 1)) is not None
