from kungfu_chess.snapshot.network_snapshot_source import NetworkSnapshotSource
from kungfu_chess.snapshot.game_snapshot import GameSnapshot


def test_network_snapshot_source_returns_latest_snapshot():

    source = NetworkSnapshotSource(None)

    snapshot = GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=[],
        selected_cell=None,
        legal_moves=set(),
        game_over=False,
    )

    source.update(snapshot)

    assert source.get_snapshot() == snapshot