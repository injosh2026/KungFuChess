from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.input.board_mapper import BoardMapper
from kungfu_chess.model.board import Board
from kungfu_chess.model.position import Position


class Controller:
    """
    Handles user input and translates it into game actions.

    The controller manages piece selection and forwards valid
    movement requests to the game engine.

    It does not validate moves or modify the board directly.
    """

    def __init__(
        self, board: Board, board_mapper: BoardMapper, game_engine: GameEngine
    ):
        """
        Creates a controller for a game session.

        Args:
            board:
                Game board.

            board_mapper:
                Converts input coordinates into board positions.

            game_engine:
                Handles movement requests.
        """
        self.board = board
        self.board_mapper = board_mapper
        self.game_engine = game_engine
        self._selected_position = None

    @property
    def selected_position(self) -> Position | None:
        return self._selected_position

    @property
    def legal_moves(self):
        if self._selected_position is None:
            return set()

        piece = self.board.get_piece_by_position(self._selected_position)
        if piece is not None and self.game_engine.is_piece_in_cooldown(piece.id):
            return set()

        return self.game_engine.get_legal_moves(
            self._selected_position
        )

    def handle_click(self, x: int, y: int):
        """
        Processes a mouse click.

        Depending on the current selection state, the click may:

        - clear the current selection,
        - select a piece,
        - request a movement.

        Args:
            x:
                Horizontal pixel coordinate.

            y:
                Vertical pixel coordinate.

        Returns:
            MoveResult if a move was requested,
            otherwise None.
        """
        position = self.board_mapper.pixel_to_position(self.board, x, y)

        if position is None:
            if self._selected_position is not None:
                self._selected_position = None

            return None

        if self._selected_position is None:

            piece = self.board.get_piece_by_position(position)

            if piece is None:
                return None

            if self.game_engine.is_piece_in_cooldown(piece.id):
                return None

            self._selected_position = position
            return None

        source = self._selected_position
        self._selected_position = None

        return self.game_engine.request_move(source, position)