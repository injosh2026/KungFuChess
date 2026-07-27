from kungfu_chess.network.snapshot_deserializer import SnapshotDeserializer
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_color import Color


def test_snapshot_deserializer_creates_game_snapshot():

    message = """
    {
        "type": "GAME_SNAPSHOT",
        "payload": {
            "board_width": 8,
            "board_height": 8,
            "game_over": false,
            "pieces": [
                {
                    "piece_id": 1,
                    "kind": "ROOK",
                    "color": "WHITE",
                    "position": {
                        "row": 0,
                        "col": 1
                    },
                    "state": "idle"
                }
            ]
        }
    }
    """

    snapshot = SnapshotDeserializer.deserialize(message)

    assert snapshot.board_width == 8
    assert snapshot.board_height == 8
    assert snapshot.game_over is False

    rook = snapshot.pieces[0]

    assert rook.kind == PieceKind.ROOK
    assert rook.color == Color.WHITE
    assert rook.position.row == 0
    assert rook.position.col == 1