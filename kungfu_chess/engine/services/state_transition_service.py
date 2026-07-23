from kungfu_chess.config.piece_code import piece_code
from kungfu_chess.model.piece import Piece


MAX_PASS_THROUGH_STEPS = 16


class StateTransitionService:

    def __init__(
        self,
        config_repository,
        state_transition_resolver,
        state_timer,
    ):
        self._config_repository = config_repository
        self._state_transition_resolver = state_transition_resolver
        self._state_timer = state_timer


    def transition(self, piece: Piece):

        code = piece_code(
            piece.kind,
            piece.color,
        )

        piece.state = self._state_transition_resolver.resolve(
            code,
            piece.state,
        )

        self._settle_piece_state(piece)


    def _settle_piece_state(self, piece: Piece):

        code = piece_code(
            piece.kind,
            piece.color,
        )

        for _ in range(MAX_PASS_THROUGH_STEPS):

            config = self._config_repository.load_state(
                code,
                piece.state,
            )

            if config.physics.duration_ms is not None:
                self._state_timer.start(
                    piece.id,
                    config.physics.duration_ms,
                )
                return


            next_state = self._state_transition_resolver.resolve(
                code,
                piece.state,
            )

            if next_state == piece.state:
                return

            piece.state = next_state