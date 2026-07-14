from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position
from kungfu_chess.view.game_snapshot import (
    GameSnapshot,
    PieceSnapshot,
)


class SnapshotBuilder:
    """
    Creates immutable snapshots from the mutable game state.

    SnapshotBuilder separates the game model from rendering layers
    by exposing only presentation data.
    """

    def build(
        self, game_state: GameState, selected_cell: Position | None = None
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
        pieces = []

        for piece in game_state.board.pieces_by_id.values():

            pieces.append(
                PieceSnapshot(
                    piece_id=piece.id,
                    kind=piece.kind,
                    color=piece.color,
                    position=piece.cell,
                    state=PieceState.IDLE,
                )
            )

        return GameSnapshot(
            board_width=game_state.board.width,
            board_height=game_state.board.height,
            pieces=pieces,
            selected_cell=selected_cell,
            game_over=game_state.game_over,
            winner=game_state.winner,
        )
