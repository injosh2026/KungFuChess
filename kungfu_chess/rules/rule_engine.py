from kungfu_chess.model.board import Board
from kungfu_chess.model.position import Position
from kungfu_chess.rules.move_reason import MoveReason
from kungfu_chess.rules.move_validation import MoveValidation


class RuleEngine:

    def __init__(self, rules):
        self._rules = rules

    def validate_move(
        self, board: Board, source: Position, destination: Position
    ) -> MoveValidation:

        if not board.is_inside(source) or not board.is_inside(destination):
            return MoveValidation(False, MoveReason.OUTSIDE_BOARD)

        piece = board.get_piece_by_position(source)

        if piece is None:
            return MoveValidation(False, MoveReason.EMPTY_SOURCE)

        target = board.get_piece_by_position(destination)

        if target is not None and target.color == piece.color:
            return MoveValidation(False, MoveReason.FRIENDLY_DESTINATION)

        rule = self._rules[piece.kind]

        destinations = rule.legal_destinations(board, piece)

        if destination not in destinations:
            return MoveValidation(False, MoveReason.ILLEGAL_PIECE_MOVE)

        return MoveValidation(True, MoveReason.OK)
