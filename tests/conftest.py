import kungfu_chess.engine.game_factory as game_factory_module

from tests.helpers import game_session_factory


def _create_game(board):
    return game_session_factory.create_game(board)


def pytest_configure():
    game_factory_module.GameFactory.create = staticmethod(_create_game)
