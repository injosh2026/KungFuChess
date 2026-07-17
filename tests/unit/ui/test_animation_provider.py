from types import MappingProxyType

from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position
from kungfu_chess.ui.animation_data import AnimationData
from kungfu_chess.ui.animation_provider import AnimationProvider
from kungfu_chess.view.game_snapshot import PieceSnapshot
from kungfu_chess.view.runtime_role import RuntimeRole

FPS = 4
FRAME_DURATION_MS = 250


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


def make_piece(state="idle"):
    return PieceSnapshot(
        piece_id=1,
        kind=PieceKind.QUEEN,
        color=Color.WHITE,
        position=Position(0, 0),
        state=state,
    )


def test_uses_piece_state_name_directly():
    animation = make_animation(3)
    library = FakeLibrary(animation)
    provider = AnimationProvider(library, FakeClock())

    provider.frame_for(make_piece("idle"))

    assert library.requests == [("QW", "idle")]


def test_returns_first_frame_at_zero_time():
    animation = make_animation(3)
    provider = AnimationProvider(FakeLibrary(animation), FakeClock())

    assert provider.frame_for(make_piece()) is animation.frames[0]


def test_advances_frame_with_time():
    animation = make_animation(3)
    clock = FakeClock()
    provider = AnimationProvider(FakeLibrary(animation), clock)

    clock.elapsed = FRAME_DURATION_MS

    assert provider.frame_for(make_piece()) is animation.frames[1]


def test_loops_back_to_start():
    animation = make_animation(3)
    clock = FakeClock()
    provider = AnimationProvider(FakeLibrary(animation), clock)

    clock.elapsed = FRAME_DURATION_MS * 3

    assert provider.frame_for(make_piece()) is animation.frames[0]


def test_supports_any_state_name():
    animation = make_animation(1)
    library = FakeLibrary(animation)
    provider = AnimationProvider(library, FakeClock())

    provider.frame_for(make_piece("long_rest"))

    assert library.requests == [("QW", "long_rest")]


def make_one_shot_piece(state="jump", active_ability_progress=0.0):
    return PieceSnapshot(
        piece_id=1,
        kind=PieceKind.QUEEN,
        color=Color.WHITE,
        position=Position(0, 0),
        state=state,
        runtime_progress=MappingProxyType(
            {RuntimeRole.ACTIVE_ABILITY: active_ability_progress},
        ),
    )


def test_one_shot_progress_zero_selects_first_frame():
    animation = make_animation(5, is_loop=False)
    provider = AnimationProvider(FakeLibrary(animation), FakeClock())

    frame = provider.frame_for(make_one_shot_piece(active_ability_progress=0.0))

    assert frame is animation.frames[0]


def test_one_shot_progress_middle_selects_middle_frame():
    animation = make_animation(5, is_loop=False)
    provider = AnimationProvider(FakeLibrary(animation), FakeClock())

    frame = provider.frame_for(make_one_shot_piece(active_ability_progress=0.5))

    assert frame is animation.frames[2]


def test_one_shot_progress_one_selects_last_frame():
    animation = make_animation(5, is_loop=False)
    provider = AnimationProvider(FakeLibrary(animation), FakeClock())

    frame = provider.frame_for(make_one_shot_piece(active_ability_progress=1.0))

    assert frame is animation.frames[4]


def test_looping_animation_ignores_active_ability_progress():
    animation = make_animation(3, is_loop=True)
    clock = FakeClock()
    clock.elapsed = FRAME_DURATION_MS
    provider = AnimationProvider(FakeLibrary(animation), clock)

    frame = provider.frame_for(
        make_one_shot_piece(state="idle", active_ability_progress=0.99)
    )

    assert frame is animation.frames[1]


def test_one_shot_animation_ignores_recovery_progress():
    animation = make_animation(5, is_loop=False)
    clock = FakeClock()
    clock.elapsed = FRAME_DURATION_MS * 2
    provider = AnimationProvider(FakeLibrary(animation), clock)

    piece = PieceSnapshot(
        piece_id=1,
        kind=PieceKind.QUEEN,
        color=Color.WHITE,
        position=Position(0, 0),
        state="jump",
        runtime_progress=MappingProxyType({RuntimeRole.RECOVERY: 0.5}),
    )

    frame = provider.frame_for(piece)

    assert frame is animation.frames[2]
