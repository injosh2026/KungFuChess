from kungfu_chess.config.piece_config_repository import PieceConfigRepository


class StateTransitionResolver:
    """
    Resolves the next piece state name from asset configuration.

    Given a piece code and its current state name, this resolver loads the
    matching state config and returns ``next_state_when_finished``. It does
    not apply transitions or track timers.
    """

    def __init__(self, config_repository: PieceConfigRepository):
        self._config_repository = config_repository

    def resolve(self, piece_code: str, current_state: str) -> str:
        config = self._config_repository.load_state(piece_code, current_state)
        return config.physics.next_state_when_finished
