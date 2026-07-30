from kungfu_chess.client.connection_command_sender import ConnectionCommandSender
from kungfu_chess.events.handlers.jump_request_handler import JumpRequestHandler
from kungfu_chess.events.handlers.move_request_handler import MoveRequestHandler
from kungfu_chess.events.handlers.promotion_request_handler import (
    PromotionRequestHandler,
)
from kungfu_chess.events.messages.jump_requested_message import JumpRequestedMessage
from kungfu_chess.events.messages.move_requested_message import MoveRequestedMessage
from kungfu_chess.events.messages.promotion_requested_message import (
    PromotionRequestedMessage,
)
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.network.local_transport import LocalConnection


class RecordingConnection:
    def __init__(self):
        self.sent_messages = []

    def send(self, message):
        self.sent_messages.append(message)

    def receive(self):
        return None


def test_request_move_sends_move_wire_format():
    connection = RecordingConnection()
    sender = ConnectionCommandSender(connection)

    sender.request_move(Position(0, 1), Position(2, 3))

    assert connection.sent_messages == ["MOVE 0 1 2 3"]


def test_request_jump_sends_jump_wire_format():
    connection = RecordingConnection()
    sender = ConnectionCommandSender(connection)

    sender.request_jump(5)

    assert connection.sent_messages == ["JUMP 5"]


def test_submit_pawn_promotion_choice_sends_promotion_wire_format():
    connection = RecordingConnection()
    sender = ConnectionCommandSender(connection)

    sender.submit_pawn_promotion_choice(4, PieceKind.QUEEN)

    assert connection.sent_messages == ["PROMOTION 4 QUEEN"]


def test_move_request_handler_delegates_to_connection_command_sender():
    connection = RecordingConnection()
    sender = ConnectionCommandSender(connection)
    handler = MoveRequestHandler(sender)

    handler.handle(
        MoveRequestedMessage(
            source=Position(1, 0),
            destination=Position(1, 2),
        )
    )

    assert connection.sent_messages == ["MOVE 1 0 1 2"]


def test_jump_request_handler_delegates_to_connection_command_sender():
    connection = RecordingConnection()
    sender = ConnectionCommandSender(connection)
    handler = JumpRequestHandler(sender)

    handler.handle(JumpRequestedMessage(piece_id=8))

    assert connection.sent_messages == ["JUMP 8"]


def test_promotion_request_handler_delegates_to_connection_command_sender():
    connection = RecordingConnection()
    sender = ConnectionCommandSender(connection)
    handler = PromotionRequestHandler(sender)

    handler.handle(
        PromotionRequestedMessage(
            piece_id=2,
            chosen_kind=PieceKind.KNIGHT,
        )
    )

    assert connection.sent_messages == ["PROMOTION 2 KNIGHT"]


def test_connection_command_sender_uses_sync_connection_send():
    client = LocalConnection()
    server = LocalConnection()
    client.connect_to(server)
    server.connect_to(client)

    sender = ConnectionCommandSender(client)
    sender.request_move(Position(0, 0), Position(0, 1))

    assert server.receive() == "MOVE 0 0 0 1"
