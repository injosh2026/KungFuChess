from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.realtime.motion import Motion


class ArrivalResolver:
    def __init__(self, game_state):
        self.game_state = game_state

    def resolve(self, motion: Motion):
        captured_piece = self.game_state.board.move_piece(
            motion.start,
            motion.target
        )

        if captured_piece is not None:
            if captured_piece.kind == PieceKind.KING:
                self.game_state.game_over = True

        return captured_piece