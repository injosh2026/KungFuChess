from typing import Protocol

from kungfu_chess.model.position import Position


class GameQueries(Protocol):

    def is_piece_in_cooldown(
        self,
        piece_id: int,
    ) -> bool: ...

    def get_legal_moves(
        self,
        position: Position,
    ) -> set[Position]: ...

    