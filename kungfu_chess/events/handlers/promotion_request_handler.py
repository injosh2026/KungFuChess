from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.events.messages.promotion_requested_message import (
    PromotionRequestedMessage,
)


class PromotionRequestHandler:
    """
    Handles pawn promotion requests.

    Delegates the actual promotion logic
    to the GameEngine.
    """

    def __init__(self, game_engine: GameEngine):
        self._game_engine = game_engine

    def handle(
        self,
        message: PromotionRequestedMessage,
    ):
        return self._game_engine.submit_pawn_promotion_choice(
            message.piece_id,
            message.chosen_kind,
        )