from kungfu_chess.realtime.motion import Motion
from kungfu_chess.realtime.movement_duration import (
    MovementDurationCalculator,
)


class MotionFactory:

    def create(self, piece, source, destination) -> Motion:
        duration = MovementDurationCalculator.calculate(
            source,
            destination,
        )

        return Motion(
            piece_id=piece.id,
            start=source,
            target=destination,
            duration_ms=duration,
        )