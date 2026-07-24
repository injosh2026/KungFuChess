from kungfu_chess.network.local_transport import LocalConnection


def test_local_connection_sends_message():

    client = LocalConnection()
    server = LocalConnection()

    client.connect_to(server)
    server.connect_to(client)

    message = object()

    client.send(message)

    assert server.receive() == message


def test_local_connection_returns_none_when_empty():

    connection = LocalConnection()

    assert connection.receive() is None