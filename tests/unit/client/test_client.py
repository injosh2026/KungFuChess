from kungfu_chess.client.client import Client
from kungfu_chess.network.local_transport import LocalConnection


def test_client_receives_server_message():

    client_connection = LocalConnection()
    server_connection = LocalConnection()

    client_connection.connect_to(server_connection)
    server_connection.connect_to(client_connection)

    client = Client(client_connection)

    message = object()

    server_connection.send(message)

    client.poll()

    assert client.received == [message]