from kungfu_chess.model.piece import Piece
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion import Motion


class MotionFactory:
    """
    Creates Motion objects from validated movement requests.

    MotionFactory is responsible only for creating the
    movement representation and calculating its duration.

    It does not validate movement legality, modify the board,
    or resolve collisions.
    """

    def __init__(self, duration_calculator):
        self.duration_calculator = duration_calculator

    def create(self, piece: Piece, source: Position, destination: Position) -> Motion:
        """
        Creates a motion for a piece moving from source to destination.

        Args:
            piece: The piece that will move.
            source: Starting board position.
            destination: Target board position.

        Returns:
            Motion object representing the planned movement.
        """
        duration = self.duration_calculator.calculate(
            source,
            destination,
        )

        return Motion(
            piece_id=piece.id,
            start=source,
            target=destination,
            duration_ms=duration,
        )
