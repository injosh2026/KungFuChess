from kungfu_chess.events.message_bus import MessageBus
from kungfu_chess.events.messages.move_requested_message import MoveRequestedMessage
from kungfu_chess.events.move_performed_event import MovePerformedEvent
from kungfu_chess.server.player_color import PlayerColor
from kungfu_chess.server.server_session import ServerSession


class DummyGameSession:

    def __init__(self):
        self.message_bus = MessageBus()


class DummyMessage:
    pass


class DummyMatch:

    def __init__(self):
        self.received = []

    def receive(self, player_id, message):
        self.received.append((player_id, message))


def test_server_session_stores_outgoing_messages():

    game_session = DummyGameSession()

    match = DummyMatch()

    session = ServerSession(
        match=match,
        game_session=game_session,
        player_id="player1",
        color=PlayerColor.WHITE,
    )

    message = object()

    session.send(message)

    assert session.outbox == [message]

    session = ServerSession(
        match=match,
        game_session=game_session,
        player_id="player1",
        color=PlayerColor.WHITE,
    )

    event = MovePerformedEvent(
        timestamp_ms=1000,
        piece_id=1,
        piece_code="wR",
        piece_name="rook",
        from_position=None,
        to_position=None,
        capture=None,
        promotion=None,
        jump_used=False,
    )

    game_session.message_bus.publish(event)

    assert session.outbox == [event]


def test_server_session_publishes_received_message():

    game_session = DummyGameSession()

    match = DummyMatch()

    session = ServerSession(match, game_session, "player1", PlayerColor.WHITE)

    received = []

    message = object()

    game_session.message_bus.subscribe(
        type(message),
        received.append,
    )

    message = object()

    session.receive(message)

    assert match.received == [("player1", message)]


def test_server_session_receives_message_and_publishes_to_bus():

    game_session = DummyGameSession()

    received = []

    game_session.message_bus.subscribe(
        MoveRequestedMessage,
        received.append,
    )

    match = DummyMatch()

    session = ServerSession(match, game_session, "player1", PlayerColor.WHITE)

    message = MoveRequestedMessage(
        source=None,
        destination=None,
    )

    message = object()

    session.receive(message)

    assert match.received == [("player1", message)]


def test_server_session_stores_player_color():

    game_session = DummyGameSession()

    match = DummyMatch()

    session = ServerSession(
        match=match,
        game_session=game_session,
        player_id="player1",
        color=PlayerColor.WHITE,
    )

    assert session.color == PlayerColor.WHITE
