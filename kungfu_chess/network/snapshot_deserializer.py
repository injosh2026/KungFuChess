import json

from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.snapshot.game_snapshot import (
    GameSnapshot,
    PieceSnapshot,
)


class SnapshotDeserializer:
    """
    Converts network messages into immutable GameSnapshot objects.

    This class knows only the network representation.
    It does not access GameState or game logic.
    """

    @staticmethod
    def deserialize(message: str) -> GameSnapshot:
        if not isinstance(message, str):
            return None

        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            return None

        if data.get("type") != "GAME_SNAPSHOT":
            return None
        
        payload = data["payload"]

        pieces = [
            SnapshotDeserializer._deserialize_piece(piece)
            for piece in payload["pieces"]
        ]

        return GameSnapshot(
            board_width=payload["board_width"],
            board_height=payload["board_height"],
            pieces=pieces,
            selected_cell=None,
            legal_moves=set(),
            game_over=payload["game_over"],
        )

    @staticmethod
    def _deserialize_piece(data: dict) -> PieceSnapshot:
        return PieceSnapshot(
            piece_id=data["piece_id"],
            kind=PieceKind[data["kind"]],
            color=Color[data["color"]],
            position=Position(
                row=data["position"]["row"],
                col=data["position"]["col"],
            ),
            state=data["state"],
        )