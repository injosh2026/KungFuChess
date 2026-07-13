from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.io.board_parser import BoardParser


class ScriptRunner:

    def __init__(self):
        self.board = None
        self.controller = None
        self.game_engine = None


    def load_board(self, lines):

        parser = BoardParser()

        self.board = parser.parse(lines)

        self.controller, self.game_engine = GameFactory.create(
            self.board
        )


    def handle_click(self, x: int, y: int):

        if self.controller is None:
            raise RuntimeError("Game is not initialized")

        return self.controller.handle_click(x, y)
    

    def wait(self, milliseconds: int):

        if self.game_engine is None:
            raise RuntimeError("Game is not initialized")

        return self.game_engine.wait(milliseconds)