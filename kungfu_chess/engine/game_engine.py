from kungfu_chess.engine.move_result import MoveResult
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.realtime.movement_duration import MovementDurationCalculator


class GameEngine:

    def __init__(self, game_state, rule_engine, realtime_arbiter):
        self.game_state = game_state
        self.rule_engine = rule_engine
        self.realtime_arbiter = realtime_arbiter

    def request_move(self, source, destination) -> MoveResult:

        if self.game_state.game_over:
            return MoveResult(False, "game_over")
        
        if self.realtime_arbiter.has_active_motion():
            return MoveResult(False, "motion_in_progress")
        
        validation = self.rule_engine.validate_move(
            self.game_state.board,
            source,
            destination
        )

        if not validation.is_valid:
            return MoveResult(False, validation.reason)

        piece = self.game_state.board.get_piece_by_position(source)

        if piece is None:
            raise RuntimeError("Validated move without source piece")

        duration = MovementDurationCalculator.calculate(
            source,
            destination
        )

        motion = Motion(
            piece_id=piece.id,
            start=source,
            target=destination,
            duration_ms=duration
        )

        self.realtime_arbiter.start_motion(motion)
        
        return MoveResult(True, "ok")
    
    def wait(self, milliseconds: int):
        completed_motion = self.realtime_arbiter.advance_time(milliseconds)

        if completed_motion is not None:
            return self.resolve_motion_arrival(completed_motion)

        return None

    def resolve_motion_arrival(self, motion: Motion):
        captured_piece = self.game_state.board.move_piece(
            motion.start,
            motion.target
        )

        if captured_piece is not None:
            if captured_piece.kind == PieceKind.KING:
                self.game_state.game_over = True

        return captured_piece