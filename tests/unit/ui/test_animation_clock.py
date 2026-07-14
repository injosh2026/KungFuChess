from kungfu_chess.ui.animation_clock import AnimationClock


class FakeTime:
    def __init__(self, value=0.0):
        self.value = value

    def __call__(self):
        return self.value


def test_elapsed_starts_at_zero():
    time_source = FakeTime(10.0)

    clock = AnimationClock(time_source)

    assert clock.elapsed_ms() == 0


def test_elapsed_advances_in_milliseconds():
    time_source = FakeTime(0.0)
    clock = AnimationClock(time_source)

    time_source.value = 1.5

    assert clock.elapsed_ms() == 1500


def test_reset_rebases_elapsed():
    time_source = FakeTime(0.0)
    clock = AnimationClock(time_source)

    time_source.value = 2.0
    clock.reset()
    time_source.value = 2.25

    assert clock.elapsed_ms() == 250
