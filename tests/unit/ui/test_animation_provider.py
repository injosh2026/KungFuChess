from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position
from kungfu_chess.ui.animation_data import AnimationData
from kungfu_chess.ui.animation_provider import AnimationProvider
from kungfu_chess.view.game_snapshot import PieceSnapshot

FPS = 4
FRAME_DURATION_MS = 250
MAPPING = {PieceState.IDLE: "idle"}


class FakeImage:
    pass


class FakeLibrary:
    def __init__(self, animation):
        self._animation = animation
        self.requests = []

    def get_animation(self, code, state):
        self.requests.append((code, state))
        return self._animation


class FakeClock:
    def __init__(self):
        self.elapsed = 0

    def elapsed_ms(self):
        return self.elapsed


def make_animation(frame_count, is_loop=True):
    frames = tuple(FakeImage() for _ in range(frame_count))
    return AnimationData(
        frames=frames,
        fps=FPS,
        is_loop=is_loop,
        next_state_when_finished="idle",
        speed_m_per_sec=0.0,
    )


def make_piece():
    return PieceSnapshot(
        piece_id=1,
        kind=PieceKind.QUEEN,
        color=Color.WHITE,
        position=Position(0, 0),
        state=PieceState.IDLE,
    )


def test_maps_piece_state_and_code_to_animation():
    animation = make_animation(3)
    library = FakeLibrary(animation)
    provider = AnimationProvider(library, FakeClock(), MAPPING)

    provider.frame_for(make_piece())

    assert library.requests == [("QW", "idle")]


def test_returns_first_frame_at_zero_time():
    animation = make_animation(3)
    provider = AnimationProvider(FakeLibrary(animation), FakeClock(), MAPPING)

    assert provider.frame_for(make_piece()) is animation.frames[0]


def test_advances_frame_with_time():
    animation = make_animation(3)
    clock = FakeClock()
    provider = AnimationProvider(FakeLibrary(animation), clock, MAPPING)

    clock.elapsed = FRAME_DURATION_MS

    assert provider.frame_for(make_piece()) is animation.frames[1]


def test_loops_back_to_start():
    animation = make_animation(3)
    clock = FakeClock()
    provider = AnimationProvider(FakeLibrary(animation), clock, MAPPING)

    clock.elapsed = FRAME_DURATION_MS * 3

    assert provider.frame_for(make_piece()) is animation.frames[0]
