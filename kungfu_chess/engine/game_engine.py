from kungfu_chess.engine.move_result import MoveResult


class GameEngine:

    def __init__(
        self,
        game_state,
        rule_engine
    ):
        self.game_state = game_state
        self.rule_engine = rule_engine


    def request_move(
        self,
        source,
        destination
    ) -> MoveResult:

        if self.game_state.game_over:
            return MoveResult(
                False,
                "game_over"
            )

        validation = self.rule_engine.validate_move(
            self.game_state.board,
            source,
            destination
        )

        if not validation.is_valid:
            return MoveResult(
                False,
                validation.reason
            )

        return MoveResult(
            True,
            "ok"
        )