import json

from kungfu_chess.snapshot.game_snapshot import GameSnapshot


class SnapshotSerializer:

    @staticmethod
    def serialize(snapshot: GameSnapshot) -> str:
        return json.dumps(SnapshotSerializer.to_dict(snapshot))

    @staticmethod
    def to_dict(snapshot: GameSnapshot) -> dict:
        return {
            "type": "GAME_SNAPSHOT",
            "payload": {
                "board_width": snapshot.board_width,
                "board_height": snapshot.board_height,
                "game_over": snapshot.game_over,
                "pieces": [
                    SnapshotSerializer._serialize_piece(piece)
                    for piece in snapshot.pieces
                ],
            },
        }

    @staticmethod
    def _serialize_piece(piece):
        return {
            "piece_id": piece.piece_id,
            "kind": piece.kind.name,
            "color": piece.color.name,
            "position": {
                "row": piece.position.row,
                "col": piece.position.col,
            },
            "state": piece.state,
        }
