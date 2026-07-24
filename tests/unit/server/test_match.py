import pytest

from kungfu_chess.server.match import Match
from kungfu_chess.server.player_color import PlayerColor
from kungfu_chess.server.player_connection import PlayerConnection

class DummyMessageBus:

    def __init__(self):
        self.messages = []

    def publish(self, message):
        self.messages.append(message)

class DummyGameSession:

    def __init__(self):
        self.message_bus = DummyMessageBus()


def test_match_stores_game_session():

    game_session = DummyGameSession()

    match = Match(
        match_id="match1",
        game_session=game_session,
    )

    assert match.match_id == "match1"
    assert match.game_session is game_session


def test_match_adds_player():

    match = Match(
        match_id="match1",
        game_session=DummyGameSession(),
    )

    match.add_player("player1")

    connection = match.players["player1"]

    assert connection.player_id == "player1"
    assert connection.color == PlayerColor.WHITE


def test_match_removes_player():

    match = Match(
        match_id="match1",
        game_session=DummyGameSession(),
    )

    match.add_player("player1")
    match.remove_player("player1")

    assert match.players == {}


def test_match_assigns_white_to_first_player():

    match = Match(
        match_id="match1",
        game_session=DummyGameSession(),
    )

    color = match.add_player("player1")

    assert color == PlayerColor.WHITE


def test_match_assigns_black_to_second_player():

    match = Match(
        match_id="match1",
        game_session=DummyGameSession(),
    )

    match.add_player("player1")

    color = match.add_player("player2")

    assert color == PlayerColor.BLACK


def test_match_rejects_third_player():

    match = Match(
        match_id="match1",
        game_session=DummyGameSession(),
    )

    match.add_player("player1")
    match.add_player("player2")

    try:
        match.add_player("player3")
        assert False
    except ValueError:
        assert True


def test_match_receives_message_and_publishes_to_bus():

    match = Match(
        match_id="match1",
        game_session=DummyGameSession(),
    )

    match.add_player("player1")

    message = object()

    match.receive(
        "player1",
        message,
    )

    assert match.game_session.message_bus.messages == [message]


def test_match_rejects_message_from_unknown_player():

    match = Match(
        match_id="match1",
        game_session=DummyGameSession(),
    )

    message = object()

    with pytest.raises(ValueError):
        match.receive(
            "intruder",
            message,
        )

    assert match.game_session.message_bus.messages == []