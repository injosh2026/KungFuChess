from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.io.board_parser import BoardParser
from kungfu_chess.io.board_printer import BoardPrinter


class ScriptRunner:
    """
    Executes text-based game scenarios for testing.

    ScriptRunner converts textual commands into game actions
    through the public game APIs.
    """

    def __init__(self):
        self.board = None
        self.controller = None
        self.game_engine = None
        self.board_printer = BoardPrinter()

    def load_board(self, lines):
        """
        Creates a new game from a textual board definition.

        Args:
            lines:
                Board definition lines.
        """

        parser = BoardParser()

        self.board = parser.parse(lines)

        result = GameFactory.create(self.board)

        self.controller = result[0]
        self.game_engine = result[1]

    def handle_click(self, x: int, y: int):
        """
        Sends a click command to the controller.
        """
        if self.controller is None:
            raise RuntimeError("Game is not initialized")

        return self.controller.handle_click(x, y)

    def wait(self, milliseconds: int):
        """
        Advances game time and resolves completed actions.
        """
        if self.game_engine is None:
            raise RuntimeError("Game is not initialized")

        return self.game_engine.wait(milliseconds)

    def print_board(self):

        if self.board is None:
            raise RuntimeError("Game is not initialized")

        return self.board_printer.print_board(self.board)

    def run(self, lines):
        """
        Executes a complete text scenario.

        Supported commands:
            Board
            click x y
            wait milliseconds
            print board
        """
        index = 0
        output = []

        while index < len(lines):

            line = lines[index].strip()

            if line == "":
                index += 1
                continue

            if line == "Board":
                index = self._load_board_from_script(lines, index + 1)
                continue

            if line.startswith("click"):
                _, x, y = line.split()

                self.handle_click(int(x), int(y))

                index += 1
                continue

            if line.startswith("wait"):
                _, milliseconds = line.split()

                self.wait(int(milliseconds))

                index += 1
                continue

            if line == "print board":
                output.append(self.print_board())

                index += 1
                continue

            raise ValueError(f"Unknown command: {line}")

        return output

    def _load_board_from_script(self, lines, start_index):

        board_lines = []

        index = start_index

        while index < len(lines):

            line = lines[index].strip()

            if (
                line == ""
                or line.startswith("click")
                or line.startswith("wait")
                or line == "print board"
            ):
                break

            board_lines.append(line)

            index += 1

        self.load_board(board_lines)

        return index
