from kungfu_chess.snapshot.local_snapshot_source import LocalSnapshotSource


class FakeSnapshotBuilder:

    def __init__(self):
        self.calls = []

    def build(
        self,
        game_state,
        selected_cell,
        motions,
        legal_moves,
    ):
        self.calls.append(
            (
                game_state,
                selected_cell,
                motions,
                legal_moves,
            )
        )

        return "snapshot"


class FakeGameEngine:

    def __init__(self):
        self.game_state = "game_state"

    def active_motions(self):
        return "motions"


class FakeController:

    selected_position = "selected"

    legal_moves = "legal_moves"


def test_local_snapshot_source_builds_snapshot_from_local_game():

    builder = FakeSnapshotBuilder()
    engine = FakeGameEngine()
    controller = FakeController()

    source = LocalSnapshotSource(
        snapshot_builder=builder,
        game_engine=engine,
        controller=controller,
    )

    result = source.get_snapshot()

    assert result == "snapshot"

    assert builder.calls == [
        (
            "game_state",
            "selected",
            "motions",
            "legal_moves",
        )
    ]