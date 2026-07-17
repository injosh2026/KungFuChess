from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece


class JumpRule:
    """
    Decides whether a piece may start an in-place jump action.

    JumpRule performs validation only. It does not modify game state.
    """

    def can_jump(self, game_state: GameState, piece: Piece) -> bool:
        if game_state.game_over:
            return False

        if game_state.pending_pawn_promotion is not None:
            return False

        return True
