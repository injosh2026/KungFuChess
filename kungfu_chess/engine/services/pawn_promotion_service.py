from kungfu_chess.engine.move_result import MoveResult
from kungfu_chess.engine.services.state_transition_service import StateTransitionService
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position
from kungfu_chess.rules.pawn_end_handler import PawnEndHandler
from kungfu_chess.rules.pawn_end_outcome import PendingPawnPromotion

NO_PENDING_PAWN_PROMOTION = "no_pending_pawn_promotion"
WRONG_PROMOTION_PIECE = "wrong_promotion_piece"
INVALID_PROMOTION_CHOICE = "invalid_promotion_choice"
PROMOTION_PIECE_NOT_FOUND = "promotion_piece_not_found"


class PawnPromotionService:

    def __init__(
        self,
        game_state: GameState,
        pawn_end_handler: PawnEndHandler,
        state_transition_service: StateTransitionService,
    ):
        self.game_state = game_state
        self._pawn_end_handler = pawn_end_handler
        self._state_transition_service = state_transition_service

    def apply_arrival(
        self,
        piece: Piece,
        landing_cell: Position,
    ) -> tuple[bool, PieceKind | None]:
        if self._pawn_end_handler is None:
            return False, None

        outcome = self._pawn_end_handler.resolve(
            piece,
            landing_cell,
            self.game_state.board,
        )

        if outcome.pending_choice_kinds is not None:
            self.game_state.pending_pawn_promotion = PendingPawnPromotion(
                piece_id=piece.id,
                allowed_kinds=outcome.pending_choice_kinds,
            )
            return outcome.blocks_state_transition, None

        if outcome.new_kind is None:
            return False, None

        piece.kind = outcome.new_kind
        piece.state = PieceState.IDLE
        return outcome.blocks_state_transition, outcome.new_kind

    def submit_pawn_promotion_choice(
        self,
        piece_id: int,
        chosen_kind: PieceKind,
    ) -> MoveResult:
        pending = self.game_state.pending_pawn_promotion

        if pending is None:
            return MoveResult(False, NO_PENDING_PAWN_PROMOTION)

        if pending.piece_id != piece_id:
            return MoveResult(False, WRONG_PROMOTION_PIECE)

        if chosen_kind not in pending.allowed_kinds:
            return MoveResult(False, INVALID_PROMOTION_CHOICE)

        piece = self.game_state.board.get_piece_by_id(piece_id)
        if piece is None:
            return MoveResult(False, PROMOTION_PIECE_NOT_FOUND)

        piece.kind = chosen_kind
        piece.state = PieceState.IDLE
        self.game_state.pending_pawn_promotion = None
        self._state_transition_service.transition(piece)

        return MoveResult(True, "ok")