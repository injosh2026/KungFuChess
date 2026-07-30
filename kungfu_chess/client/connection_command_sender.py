from kungfu_chess.events.messages.jump_requested_message import JumpRequestedMessage
from kungfu_chess.events.messages.move_requested_message import MoveRequestedMessage
from kungfu_chess.events.messages.promotion_requested_message import (
    PromotionRequestedMessage,
)
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.network.connection import Connection


class ConnectionCommandSender:
    """
    Sends game input commands through a Connection.

    Implements the method surface expected by request handlers so
    MoveRequestHandler, JumpRequestHandler, and PromotionRequestHandler
    can delegate outbound client input without depending on GameEngine.
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def request_move(self, source: Position, destination: Position) -> None:
        message = MoveRequestedMessage(
            source=source,
            destination=destination,
        )
        self._connection.send(message.to_wire_format())

    def request_jump(self, piece_id: int) -> None:
        message = JumpRequestedMessage(piece_id=piece_id)
        self._connection.send(message.to_wire_format())

    def submit_pawn_promotion_choice(
        self,
        piece_id: int,
        chosen_kind: PieceKind,
    ) -> None:
        message = PromotionRequestedMessage(
            piece_id=piece_id,
            chosen_kind=chosen_kind,
        )
        self._connection.send(message.to_wire_format())
