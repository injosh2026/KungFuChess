from application.game_application import GameApplication
from kungfu_chess.model import board


def test_create_game_creates_session():
    app = GameApplication()

    session = app.create_game(
        "game1",
        board,
    )

    assert session is not None
    assert session.controller is not None
    assert session.game_engine is not None
    assert session.move_history is not None
    assert session.score is not None


def test_get_game_returns_created_session():
    app = GameApplication()

    created = app.create_game("game1", board)

    loaded = app.get_game("game1")

    assert loaded is created