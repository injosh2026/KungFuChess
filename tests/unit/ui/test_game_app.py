from types import SimpleNamespace

import pytest

from kungfu_chess.ui.game_app import PRESENT_WAIT_MS, GameApp

STOP_AFTER = 3
CLOCK_SEQUENCE = [0, 10, 25, 45]
EXPECTED_DELTAS = [10, 15, 20]
GAME_STATE = object()
SELECTED = object()


class FakeCanvas:
    def __init__(self, stop_after):
        self.presents = []
        self._stop_after = stop_after

    def present(self, wait_ms=1):
        self.presents.append(wait_ms)
        if len(self.presents) >= self._stop_after:
            raise KeyboardInterrupt


class FakeImage:
    def __init__(self):
        self.opened = False
        self.closed = False

    def open_window(self):
        self.opened = True

    def close(self):
        self.closed = True


class FakeRenderer:
    def __init__(self, canvas):
        self._canvas = canvas
        self.snapshots = []

    def render(self, snapshot):
        self.snapshots.append(snapshot)
        return self._canvas


class FakeSnapshotBuilder:
    def __init__(self):
        self.calls = []

    def build(self, game_state, selected_cell=None, motion=None):
        self.calls.append((game_state, selected_cell, motion))
        return ("snapshot", len(self.calls))


class FakeGameEngine:
    def __init__(self, game_state):
        self.game_state = game_state
        self.realtime_arbiter = SimpleNamespace(
            active_motion=None
        )
        self.waits = []

    def wait(self, milliseconds):
        self.waits.append(milliseconds)
        return []


class FakeController:
    def __init__(self, selected):
        self._selected = selected

    @property
    def selected_position(self):
        return self._selected


class FakeClock:
    def __init__(self, sequence):
        self._sequence = list(sequence)
        self.reads = 0

    def elapsed_ms(self):
        value = self._sequence[self.reads]
        self.reads += 1
        return value


class RaisingRenderer:
    def render(self, snapshot):
        raise ValueError("render failure")


def make_app(stop_after=STOP_AFTER, selected=SELECTED):
    canvas = FakeCanvas(stop_after)
    image = FakeImage()
    renderer = FakeRenderer(canvas)
    builder = FakeSnapshotBuilder()
    engine = FakeGameEngine(GAME_STATE)
    controller = FakeController(selected)
    clock = FakeClock(CLOCK_SEQUENCE)

    app = GameApp(engine, controller, builder, renderer, image, clock, object())

    return app, canvas, image, renderer, builder, engine


def test_opens_and_closes_window():
    app, _, image, _, _, _ = make_app()

    app.run()

    assert image.opened is True
    assert image.closed is True


def test_advances_engine_with_time_deltas():
    app, _, _, _, _, engine = make_app()

    app.run()

    assert engine.waits == EXPECTED_DELTAS


def test_builds_snapshot_from_state_and_selection():
    app, _, _, _, builder, _ = make_app()

    app.run()

    assert builder.calls == [(GAME_STATE, SELECTED, None)] * STOP_AFTER


def test_renders_and_presents_each_iteration():
    app, canvas, _, renderer, _, _ = make_app()

    app.run()

    assert len(renderer.snapshots) == STOP_AFTER
    assert canvas.presents == [PRESENT_WAIT_MS] * STOP_AFTER


def test_closes_window_on_unexpected_error():
    image = FakeImage()
    engine = FakeGameEngine(GAME_STATE)
    app = GameApp(
        engine,
        FakeController(SELECTED),
        FakeSnapshotBuilder(),
        RaisingRenderer(),
        image,
        FakeClock(CLOCK_SEQUENCE),
        object(),
    )

    with pytest.raises(ValueError):
        app.run()

    assert image.closed is True
