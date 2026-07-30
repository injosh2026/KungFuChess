from types import SimpleNamespace

from kungfu_chess.model.position import Position
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


def test_network_snapshot_source_returns_none_before_first_update():
    source = NetworkSnapshotSource(None)

    assert source.get_snapshot() is None


def test_network_snapshot_source_overlays_controller_selection():
    controller = SimpleNamespace(
        selected_position=Position(1, 2),
        legal_moves={Position(2, 2), Position(3, 2)},
    )

    source = NetworkSnapshotSource(None, controller=controller)

    server_snapshot = GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=[],
        selected_cell=Position(0, 0),
        legal_moves={Position(0, 1)},
        game_over=False,
    )

    source.update(server_snapshot)

    snapshot = source.get_snapshot()

    assert snapshot.selected_cell == Position(1, 2)
    assert snapshot.legal_moves == {Position(2, 2), Position(3, 2)}
    assert snapshot.board_width == server_snapshot.board_width
    assert snapshot.pieces == server_snapshot.pieces


def test_network_snapshot_source_without_controller_keeps_server_selection():
    source = NetworkSnapshotSource(None)

    server_snapshot = GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=[],
        selected_cell=Position(4, 4),
        legal_moves={Position(5, 4)},
        game_over=False,
    )

    source.update(server_snapshot)

    assert source.get_snapshot() == server_snapshot


def test_network_snapshot_source_does_not_mutate_controller_board():
    board = object()
    controller = SimpleNamespace(
        board=board,
        selected_position=Position(0, 0),
        legal_moves=set(),
    )

    source = NetworkSnapshotSource(None, controller=controller)

    source.update(
        GameSnapshot(
            board_width=8,
            board_height=8,
            pieces=[],
            selected_cell=None,
            legal_moves=set(),
            game_over=False,
        )
    )

    source.get_snapshot()

    assert controller.board is board
