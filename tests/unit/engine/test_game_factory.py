from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.input.controller import Controller
from kungfu_chess.model.board import Board


def test_factory_creates_controller_and_engine():

    board = Board(8, 8)

    controller, engine = GameFactory.create(board)

    assert isinstance(controller, Controller)
    assert isinstance(engine, GameEngine)


def test_factory_connects_same_board():

    board = Board(8, 8)

    controller, engine = GameFactory.create(board)

    assert controller.board is board
    assert engine.game_state.board is board


def test_factory_creates_engine_with_empty_realtime_state():

    board = Board(8, 8)

    _, engine = GameFactory.create(board)

    assert engine.realtime_arbiter.has_active_motion() is False