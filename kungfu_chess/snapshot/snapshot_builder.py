from collections.abc import Callable, Iterable, Mapping, Sequence
from types import MappingProxyType

from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.position import Position
from kungfu_chess.view.visual_position import VisualPositionCalculator
from kungfu_chess.snapshot.game_snapshot import (
    EMPTY_RUNTIME_PROGRESS,
    GameSnapshot,
    PieceSnapshot,
    PromotionSnapshot,
)
from kungfu_chess.snapshot.visual_position_overlay import (
    index_motions_by_piece_id,
    visual_position_for_piece,
)
from kungfu_chess.view.move_history_entry import MoveHistoryEntry
from kungfu_chess.view.runtime_role import RuntimeRole


class SnapshotBuilder:
    """
    Creates immutable snapshots from the mutable game state.

    SnapshotBuilder separates the game model from rendering layers
    by exposing only presentation data.

    Piece ``state`` always comes from ``Piece.state``. Active motions
    affect only ``visual_position``; they never override or infer the
    piece state name.
    """

    def __init__(
        self,
        visual_position_calculator=None,
        get_runtime_progress: Callable[
            [int], Mapping[RuntimeRole, float]
        ] | None = None,
        get_move_history: Callable[[], Sequence[MoveHistoryEntry]] | None = None,
        get_player_scores: Callable[[], Mapping[str, int]] | None = None,
    ):
        self._visual_position_calculator = (
            visual_position_calculator or VisualPositionCalculator(100)
        )
        self._get_runtime_progress = get_runtime_progress or (
            lambda _piece_id: EMPTY_RUNTIME_PROGRESS
        )
        self._get_move_history = get_move_history or (lambda: ())
        self._get_player_scores = get_player_scores or (lambda: {})

    def build(
        self,
        game_state: GameState,
        selected_cell: Position | None = None,
        motions: Iterable | None = None,
        legal_moves: set[Position] | None = None,
    ) -> GameSnapshot:
        """
        Builds a snapshot representing the current game state.

        Args:
            game_state:
                Current mutable game state.
            selected_cell:
                Currently selected board cell, if any.
            motions:
                Optional active motions used only for visual interpolation.
                They do not change ``PieceSnapshot.state``.
            legal_moves:
                Legal destination cells for the current selection.
        """
        motion_by_piece_id = index_motions_by_piece_id(motions)

        pieces = []

        for piece in game_state.board.pieces_by_id.values():
            visual_position = visual_position_for_piece(
                piece.id,
                motion_by_piece_id,
                self._visual_position_calculator,
            )

            pieces.append(
                PieceSnapshot(
                    piece_id=piece.id,
                    kind=piece.kind,
                    color=piece.color,
                    position=piece.cell,
                    state=piece.state,
                    visual_position=visual_position,
                    runtime_progress=self._immutable_runtime_progress(
                        self._get_runtime_progress(piece.id),
                    ),
                )
            )

        if legal_moves is None:
            legal_moves = set()

        pending_promotion = self._build_pending_promotion(game_state)

        return GameSnapshot(
            board_width=game_state.board.width,
            board_height=game_state.board.height,
            pieces=pieces,
            selected_cell=selected_cell,
            legal_moves=legal_moves,
            game_over=game_state.game_over,
            winner=game_state.winner,
            pending_promotion=pending_promotion,
            move_history=tuple(self._get_move_history()),
            player_scores=MappingProxyType(dict(self._get_player_scores())),
        )

    @staticmethod
    def _immutable_runtime_progress(
        runtime_progress: Mapping[RuntimeRole, float],
    ) -> Mapping[RuntimeRole, float]:
        if not runtime_progress:
            return EMPTY_RUNTIME_PROGRESS

        return MappingProxyType(dict(runtime_progress))

    @staticmethod
    def _build_pending_promotion(game_state: GameState) -> PromotionSnapshot | None:
        pending = game_state.pending_pawn_promotion
        if pending is None:
            return None

        piece = game_state.board.get_piece_by_id(pending.piece_id)
        if piece is None:
            return None

        return PromotionSnapshot(
            piece_id=pending.piece_id,
            position=piece.cell,
            color=piece.color,
            allowed_kinds=pending.allowed_kinds,
        )
