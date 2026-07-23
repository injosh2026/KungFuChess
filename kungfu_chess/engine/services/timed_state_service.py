from kungfu_chess.config.piece_code import piece_code
from kungfu_chess.model.game_state import GameState

MAX_PASS_THROUGH_STEPS = 16


class TimedStateService:

    def __init__(
        self,
        game_state: GameState,
        state_timer,
        jump_window_tracker,
        config_repository,
        state_transition_service,
    ):
        self._game_state = game_state
        self._state_timer = state_timer
        self._jump_window_tracker = jump_window_tracker
        self._config_repository = config_repository
        self._state_transition_service = state_transition_service

    def advance(self, milliseconds: int):

        active_timers = frozenset(self._state_timer.active_piece_ids())

        for piece_id in self._jump_window_tracker.advance(milliseconds):
            piece = self._game_state.board.pieces_by_id.get(piece_id)

            if piece is None:
                continue

            code = piece_code(
                piece.kind,
                piece.color,
            )

            if piece.state == self._config_repository.get_jump_command_state(code):
                self._state_transition_service.transition(piece)

        for piece_id in self._state_timer.advance(
            milliseconds,
            only_piece_ids=active_timers,
        ):
            piece = self._game_state.board.pieces_by_id.get(piece_id)

            if piece is not None:
                self._state_transition_service.transition(piece)

   