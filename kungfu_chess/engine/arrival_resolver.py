from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
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

    def resolve(self, motion: Motion, *, arrival_cell: Position | None = None):
        """
        Applies a completed motion to the board.

        The moving piece is placed on the target position, or on
        arrival_cell when a friendly-block bounce is resolved.

        If another piece occupies the landing cell, that piece
        is removed and returned as the captured piece.

        Currently, capturing a king ends the game.

        Args:
            motion:
                Completed movement information.
            arrival_cell:
                Optional resolved landing cell. When None, motion.target
                is used.

        Returns:
            The captured piece if a capture occurred,
            otherwise None.
        """
        destination = arrival_cell if arrival_cell is not None else motion.target

        captured_piece = self.game_state.board.move_piece(
            motion.start,
            destination,
        )

        if captured_piece and captured_piece.kind == PieceKind.KING:
                self.game_state.game_over = True

        return captured_piece