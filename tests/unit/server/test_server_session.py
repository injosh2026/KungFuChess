from kungfu_chess.events.message_bus import MessageBus
from kungfu_chess.events.messages.move_requested_message import MoveRequestedMessage
from kungfu_chess.events.motion_started_event import MotionStartedEvent
from kungfu_chess.events.move_performed_event import MovePerformedEvent
from kungfu_chess.model.position import Position
from kungfu_chess.server.player_color import PlayerColor
from kungfu_chess.server.server_session import ServerSession


class DummySnapshotBuilder:

    def build(self, game_state):
        from kungfu_chess.snapshot.game_snapshot import GameSnapshot

        return GameSnapshot(
            board_width=8,
            board_height=8,
            pieces=[],
            selected_cell=None,
            legal_moves=set(),
            game_over=False,
        )


class DummyGameEngine:

    def __init__(self):
        self.game_state = object()


class DummyGameSession:

    def __init__(self):
        self.message_bus = MessageBus()
        self.snapshot_builder = DummySnapshotBuilder()
        self.game_engine = DummyGameEngine()


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

    assert len(session.outbox) == 1
    assert "GAME_SNAPSHOT" in session.outbox[0]


def test_server_session_sends_motion_started_on_event():
    game_session = DummyGameSession()
    match = DummyMatch()

    session = ServerSession(
        match=match,
        game_session=game_session,
        player_id="player1",
        color=PlayerColor.WHITE,
    )

    event = MotionStartedEvent(
        timestamp_ms=250,
        piece_id=1,
        start=Position(0, 0),
        target=Position(0, 1),
        duration_ms=1000,
        state="move",
    )

    game_session.message_bus.publish(event)

    assert len(session.outbox) == 1
    assert "MOTION_STARTED" in session.outbox[0]
    assert '"piece_id": 1' in session.outbox[0]
    assert '"duration_ms": 1000' in session.outbox[0]
    assert '"state": "move"' in session.outbox[0]
    assert '"timestamp_ms": 250' in session.outbox[0]


def test_all_server_sessions_receive_same_motion_started_message():
    game_session = DummyGameSession()
    match = DummyMatch()

    white_session = ServerSession(
        match=match,
        game_session=game_session,
        player_id="player1",
        color=PlayerColor.WHITE,
    )
    black_session = ServerSession(
        match=match,
        game_session=game_session,
        player_id="player2",
        color=PlayerColor.BLACK,
    )

    event = MotionStartedEvent(
        timestamp_ms=0,
        piece_id=1,
        start=Position(2, 3),
        target=Position(4, 3),
        duration_ms=1200,
        state="move",
    )

    game_session.message_bus.publish(event)

    assert len(white_session.outbox) == 1
    assert len(black_session.outbox) == 1
    assert white_session.outbox[0] == black_session.outbox[0]
    assert "MOTION_STARTED" in white_session.outbox[0]


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
