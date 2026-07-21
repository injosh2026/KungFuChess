from kungfu_chess.input.game_queries import GameQueries
from kungfu_chess.events.message_bus import MessageBus
from kungfu_chess.events.messages.jump_requested_message import JumpRequestedMessage
from kungfu_chess.events.messages.move_requested_message import (
    MoveRequestedMessage,
)
from kungfu_chess.events.messages.promotion_requested_message import PromotionRequestedMessage
from kungfu_chess.input.board_mapper import BoardMapper
from kungfu_chess.input.jump_command import JumpCommand
from kungfu_chess.input.promote_pawn_command import PromotePawnCommand
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
        self,
        board: Board,
        board_mapper: BoardMapper,
        game_queries: GameQueries,
        message_bus: MessageBus,
    ):
        """
        Creates a controller for a game session.
        Args:
            board:
                Game board.

            board_mapper:
                Converts input coordinates into board positions.

            game_queries:
                Handles movement requests.
        """
        self.board = board
        self.board_mapper = board_mapper
        self.game_queries = game_queries
        self.message_bus = message_bus
        self._selected_position = None

    @property
    def selected_position(self) -> Position | None:
        return self._selected_position

    @property
    def legal_moves(self):
        if self._selected_position is None:
            return set()

        piece = self.board.get_piece_by_position(self._selected_position)
        if piece is not None and self.game_queries.is_piece_in_cooldown(piece.id):
            return set()

        return self.game_queries.get_legal_moves(self._selected_position)

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

            if self.game_queries.is_piece_in_cooldown(piece.id):
                return None

            self._selected_position = position
            return None

        source = self._selected_position
        self._selected_position = None

        if source == position:
            piece = self.board.get_piece_by_position(source)
            if piece is None:
                return None

            return self.handle_jump(JumpCommand(piece_id=piece.id))

        message = MoveRequestedMessage(
            source=source,
            destination=position,
        )
        self.message_bus.publish(message)
        return None

    def handle_jump(self, command: JumpCommand):
        """
        Publishes a jump request message.

        Args:
            command:
                Jump request data from input.

        Returns:
            None.
        """
        message = JumpRequestedMessage(piece_id=command.piece_id)

        self.message_bus.publish(message)

    def handle_promotion_choice(self, command: PromotePawnCommand):
        """
        Forwards a pawn promotion choice to the game engine.

        Args:
            command:
                Promotion choice data from input.

        Returns:
            MoveResult from the game engine.
        """
        message = PromotionRequestedMessage(
            piece_id=command.piece_id,
            chosen_kind=command.chosen_kind,
        )

        self.message_bus.publish(message)
