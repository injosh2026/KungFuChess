from kungfu_chess.model.board import Board
from kungfu_chess.model.position import Position
from kungfu_chess.rules.move_reason import MoveReason
from kungfu_chess.rules.move_validation import MoveValidation


class RuleEngine:
    """
    Validates movement requests according to configured piece rules.

    RuleEngine does not modify the board or perform moves.
    It only checks whether a requested movement is legal.
    """

    def __init__(self, rules):
        """
        Creates a rule engine.

        Args:
            rules: Mapping between piece types and their movement rules.
        """

        self._rules = rules

    def validate_move(
        self, board: Board, source: Position, destination: Position
    ) -> MoveValidation:
        """
        Validates whether a piece can move from source to destination.

        Args:
            board: Current game board.
            source: Starting position.
            destination: Requested destination.

        Returns:
            MoveValidation containing validation result and reason.
        """

        if not board.is_inside(source) or not board.is_inside(destination):
            return MoveValidation(False, MoveReason.OUTSIDE_BOARD)

        piece = board.get_piece_by_position(source)

        if piece is None:
            return MoveValidation(False, MoveReason.EMPTY_SOURCE)

        target = board.get_piece_by_position(destination)

        if target is not None and target.color == piece.color:
            return MoveValidation(False, MoveReason.FRIENDLY_DESTINATION)

        rule = self._rules.get(piece.kind)

        if rule is None:
            return MoveValidation(False, MoveReason.UNKNOWN_PIECE_RULE)

        destinations = rule.legal_destinations(board, piece)

        if destination not in destinations:
            return MoveValidation(False, MoveReason.ILLEGAL_PIECE_MOVE)

        return MoveValidation(True, MoveReason.OK)
