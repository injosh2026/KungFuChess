import asyncio

from kungfu_chess.client.client import Client
from kungfu_chess.client.client_session import ClientSession
from kungfu_chess.network.local_transport import LocalConnection
from kungfu_chess.snapshot.network_snapshot_source import NetworkSnapshotSource


def test_client_receives_server_message():

    client_connection = LocalConnection()
    server_connection = LocalConnection()

    client_connection.connect_to(server_connection)
    server_connection.connect_to(client_connection)

    session = ClientSession(
        "player1",
        client_connection,
        NetworkSnapshotSource(client_connection),
    )

    client = Client(session)

    message = object()

    server_connection.send(message)

    asyncio.run(client.listen_once())

    assert client.messages == [message]
