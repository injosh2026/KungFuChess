import asyncio

from kungfu_chess.client.client import Client
from kungfu_chess.client.client_session import ClientSession
from kungfu_chess.network.local_transport import LocalConnection
from kungfu_chess.network.snapshot_serializer import SnapshotSerializer
from kungfu_chess.snapshot.network_snapshot_source import NetworkSnapshotSource
from kungfu_chess.snapshot.game_snapshot import GameSnapshot


def test_client_background_listener_updates_snapshot_source():

    client_connection = LocalConnection()
    server_connection = LocalConnection()

    client_connection.connect_to(server_connection)
    server_connection.connect_to(client_connection)

    source = NetworkSnapshotSource(
        client_connection,
    )

    session = ClientSession(
        "player1",
        client_connection,
        source,
    )

    client = Client(session)

    snapshot = GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=[],
        selected_cell=None,
        legal_moves=set(),
        game_over=False,
    )

    server_connection.send(
        SnapshotSerializer.serialize(snapshot)
    )

    asyncio.run(
        client.listen_once()
    )

    assert source.get_snapshot() == snapshot