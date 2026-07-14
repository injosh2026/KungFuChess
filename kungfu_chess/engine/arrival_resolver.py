from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.realtime.motion import Motion


class ArrivalResolver:
    """
    Resolves completed motions and applies their effects to the game state.

    ArrivalResolver is responsible for updating the board when
    a piece reaches its destination and returning any captured piece.

    It does not validate movement legality or create motions.
    """

    def __init__(self, game_state: GameState):
        """
        Creates an arrival resolver.

        Args:
            game_state:
                Current mutable state of the game.
        """
        self.game_state = game_state

    def resolve(self, motion: Motion):
        """
        Applies a completed motion to the board.

        The moving piece is placed on the target position.
        If another piece occupies the target position, that piece
        is removed and returned as the captured piece.

        Currently, capturing a king ends the game.

        Args:
            motion:
                Completed movement information.

        Returns:
            The captured piece if a capture occurred,
            otherwise None.
        """
        captured_piece = self.game_state.board.move_piece(
            motion.start,
            motion.target
        )

        if captured_piece and captured_piece.kind == PieceKind.KING:
                self.game_state.game_over = True

        return captured_piece