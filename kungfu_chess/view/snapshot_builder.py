from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.view.game_snapshot import (
    GameSnapshot,
    PieceSnapshot,
)


CELL_SIZE = 100


class SnapshotBuilder:

    def build(self, game_state, selected_cell=None) -> GameSnapshot:

        pieces = []

        for piece in game_state.board.pieces_by_id.values():

            pixel_position = (
                piece.cell.col * CELL_SIZE,
                piece.cell.row * CELL_SIZE
            )

            pieces.append(
                PieceSnapshot(
                    piece_id=piece.id,
                    kind=piece.kind,
                    color=piece.color,
                    pixel_position=pixel_position,
                    state=PieceState.IDLE
                )
            )

        return GameSnapshot(
            board_width=game_state.board.width,
            board_height=game_state.board.height,
            pieces=pieces,
            selected_cell=selected_cell,
            game_over=game_state.game_over
        )