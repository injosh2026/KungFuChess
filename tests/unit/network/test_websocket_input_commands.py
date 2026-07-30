import pytest

from kungfu_chess.events.messages.jump_requested_message import JumpRequestedMessage
from kungfu_chess.events.messages.move_requested_message import MoveRequestedMessage
from kungfu_chess.events.messages.promotion_requested_message import (
    PromotionRequestedMessage,
)
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.network.websocket_server import WebSocketServer


class RecordingSession:
    def __init__(self):
        self.received = []

    def receive(self, message):
        self.received.append(message)


def test_parse_input_command_move():
    message = WebSocketServer._parse_input_command("MOVE 0 1 2 3")

    assert message == MoveRequestedMessage(
        source=Position(0, 1),
        destination=Position(2, 3),
    )


def test_parse_input_command_jump():
    message = WebSocketServer._parse_input_command("JUMP 7")

    assert message == JumpRequestedMessage(piece_id=7)


def test_parse_input_command_promotion():
    message = WebSocketServer._parse_input_command("PROMOTION 4 QUEEN")

    assert message == PromotionRequestedMessage(
        piece_id=4,
        chosen_kind=PieceKind.QUEEN,
    )


def test_parse_input_command_returns_none_for_unknown_text():
    assert WebSocketServer._parse_input_command("hello") is None


def test_parse_input_command_rejects_invalid_move_format():
    with pytest.raises(ValueError):
        WebSocketServer._parse_input_command("MOVE 0 0")


def test_receive_input_command_forwards_move_to_session():
    server = WebSocketServer(game_server=None)
    session = RecordingSession()
    server.sessions["white"] = session

    handled = server.receive_input_command("white", "MOVE 1 0 1 2")

    assert handled is True
    assert session.received == [
        MoveRequestedMessage(
            source=Position(1, 0),
            destination=Position(1, 2),
        )
    ]


def test_receive_input_command_forwards_jump_to_session():
    server = WebSocketServer(game_server=None)
    session = RecordingSession()
    server.sessions["black"] = session

    handled = server.receive_input_command("black", "JUMP 9")

    assert handled is True
    assert session.received == [JumpRequestedMessage(piece_id=9)]


def test_receive_input_command_forwards_promotion_to_session():
    server = WebSocketServer(game_server=None)
    session = RecordingSession()
    server.sessions["white"] = session

    handled = server.receive_input_command("white", "PROMOTION 2 KNIGHT")

    assert handled is True
    assert session.received == [
        PromotionRequestedMessage(
            piece_id=2,
            chosen_kind=PieceKind.KNIGHT,
        )
    ]


def test_receive_input_command_returns_false_for_unknown_text():
    server = WebSocketServer(game_server=None)
    session = RecordingSession()
    server.sessions["white"] = session

    handled = server.receive_input_command("white", "UNKNOWN 1")

    assert handled is False
    assert session.received == []
