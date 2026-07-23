
from kungfu_chess.config.state_config import GraphicsConfig, PhysicsConfig, StateConfig
from kungfu_chess.realtime.motion import Motion


class FixedJumpDurationResolver:

    def __init__(self, duration_ms: int):
        self._duration_ms = duration_ms

    def duration_ms(self, piece_code, jump_state_name):
        return self._duration_ms


class JumpLifecycleTransitionResolver:

    def resolve(self, piece_code, current_state):
        if current_state == "jump":
            return "short_rest"
        if current_state == "short_rest":
            return "idle"
        return current_state


class FakeRuleEngine:

    def __init__(self, validation):
        self.validation = validation
        self.called = False

    def validate_move(self, board, source, destination):
        self.called = True
        return self.validation


class FakeArbiter:

    def __init__(self):
        self.called_with = None

    def active_motions(self):
        return ()

    def advance_time(self, milliseconds):
        self.called_with = milliseconds
        return []


class FakeMotionFactory:

    def create(self, piece, source, target):
        return Motion(piece.id, source, target, 1000)


class TrackingMotionFactory:

    def __init__(self):
        self.calls = []

    def create(self, piece, source, target):
        self.calls.append((piece.id, source, target))
        return Motion(
            piece.id,
            source,
            target,
            duration_ms=1000,
        )


class FakeConfigRepository:

    def __init__(self, move_command_state="move", jump_command_state="jump"):
        self.move_command_state = move_command_state
        self.jump_command_state = jump_command_state

    def get_move_command_state(self, piece_code):
        return self.move_command_state

    def get_jump_command_state(self, piece_code):
        return self.jump_command_state

    def load_state(self, piece_code, state_name):
        if state_name == "jump":
            return StateConfig(
                physics=PhysicsConfig(
                    speed_m_per_sec=3.0,
                    next_state_when_finished="short_rest",
                ),
                graphics=GraphicsConfig(frames_per_sec=8, is_loop=False),
            )

        if state_name == "short_rest":
            return StateConfig(
                physics=PhysicsConfig(
                    speed_m_per_sec=0.0,
                    next_state_when_finished="idle",
                    duration_ms=1500,
                ),
                graphics=GraphicsConfig(frames_per_sec=8, is_loop=True),
            )

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


class TrackingStateTransitionResolver:

    def __init__(self, next_state="idle"):
        self.calls = []
        self.next_state = next_state

    def resolve(self, piece_code, current_state):
        self.calls.append((piece_code, current_state))
        return self.next_state


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

