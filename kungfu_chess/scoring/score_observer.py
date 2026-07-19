from collections.abc import Mapping
from types import MappingProxyType

from kungfu_chess.config.piece_code import KIND_CODES
from kungfu_chess.events.game_event import GameEvent
from kungfu_chess.events.move_performed_event import MovePerformedEvent
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.scoring.piece_values import piece_value

KIND_BY_CODE = {code: kind for kind, code in KIND_CODES.items()}


def player_id_from_piece_code(piece_code: str) -> str:
    return piece_code[-1]


def kind_from_piece_code(piece_code: str) -> PieceKind:
    return KIND_BY_CODE[piece_code[0]]


class ScoreObserver:
    """
    Updates player scores from completed captures in MovePerformedEvent.

    Scores are keyed by generic player identifiers taken from the moving
    piece code. The observer does not know about rendering.
    """

    def __init__(self) -> None:
        self._scores: dict[str, int] = {}

    def on_game_event(self, event: GameEvent) -> None:
        if not isinstance(event, MovePerformedEvent):
            return

        if event.capture is None:
            return

        player_id = player_id_from_piece_code(event.piece_code)
        captured_kind = kind_from_piece_code(event.capture)
        self._scores[player_id] = (
            self._scores.get(player_id, 0) + piece_value(captured_kind)
        )

    def scores(self) -> Mapping[str, int]:
        return MappingProxyType(dict(self._scores))
