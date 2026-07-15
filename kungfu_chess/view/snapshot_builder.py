from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position
from kungfu_chess.view.visual_position import VisualPositionCalculator
from kungfu_chess.view.game_snapshot import (
    GameSnapshot,
    MotionSnapshot,
    PieceSnapshot,
)


class SnapshotBuilder:
    """
    Creates immutable snapshots from the mutable game state.

    SnapshotBuilder separates the game model from rendering layers
    by exposing only presentation data.
    """

    def __init__(self, visual_position_calculator=None):
        self._visual_position_calculator = (
            visual_position_calculator or VisualPositionCalculator(100)
        )

    def build(
        self,
        game_state: GameState,
        selected_cell: Position | None = None,
        motion=None,
    ) -> GameSnapshot:
        """
        Builds a snapshot representing the current game state.

        Args:
            game_state:
                Current mutable game state.
            selected_cell:
                Currently selected board cell, if any.

        Returns:
            Immutable snapshot for rendering.
        """
        motion_snapshot = None

        if motion:
            motion_snapshot = MotionSnapshot(
                piece_id=motion.piece_id,
                start=motion.start,
                target=motion.target,
                progress=min(motion.elapsed_ms / motion.duration_ms, 1.0),
            )

        pieces = []

        for piece in game_state.board.pieces_by_id.values():

            visual_position = None

            if motion_snapshot and motion_snapshot.piece_id == piece.id:
                visual_position = self._visual_position_calculator.calculate(
                    motion_snapshot.start,
                    motion_snapshot.target,
                    motion_snapshot.progress,
                )

            pieces.append(
                PieceSnapshot(
                    piece_id=piece.id,
                    kind=piece.kind,
                    color=piece.color,
                    position=piece.cell,
                    state=PieceState.IDLE,
                    visual_position=visual_position,
                )
            )

        return GameSnapshot(
            board_width=game_state.board.width,
            board_height=game_state.board.height,
            pieces=pieces,
            selected_cell=selected_cell,
            game_over=game_state.game_over,
            active_motion=motion_snapshot,
            winner=game_state.winner,
        )
