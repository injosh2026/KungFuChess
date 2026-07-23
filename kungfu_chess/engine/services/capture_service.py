from kungfu_chess.engine.jump_window_tracker import JumpWindowTracker
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.engine.collision_decisions import CellOccupant
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter


class CaptureService:

    def __init__(
        self,
        game_state: GameState,
        realtime_arbiter: RealTimeArbiter,
        jump_window_tracker: JumpWindowTracker,
    ):
        self._game_state = game_state
        self._realtime_arbiter = realtime_arbiter
        self._jump_window_tracker = jump_window_tracker

    def capture(
        self,
        victim_piece_id: int,
        occupied_cells: dict[Position, CellOccupant],
        captured_pieces: list[Piece],
    ) -> None:
        victim = self._game_state.board.get_piece_by_id(victim_piece_id)
        if victim is None:
            return

        self._game_state.board.remove_piece(victim.cell)
        self._realtime_arbiter.cancel_motion(victim.id)
        self._jump_window_tracker.clear(victim.id)

        if victim.kind == PieceKind.KING:
            self._game_state.game_over = True

        captured_pieces.append(victim)

        for cell, occupant in list(occupied_cells.items()):
            if occupant.piece_id == victim.id:
                del occupied_cells[cell]