import json

from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position
from kungfu_chess.snapshot.game_snapshot import GameSnapshot, PieceSnapshot
from kungfu_chess.network.snapshot_serializer import SnapshotSerializer


def test_snapshot_serializer_creates_game_snapshot_message():

    snapshot = GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=[],
        selected_cell=None,
        legal_moves=set(),
        game_over=False,
    )

    result = SnapshotSerializer.serialize(snapshot)

    data = json.loads(result)

    assert data["type"] == "GAME_SNAPSHOT"
    assert data["payload"]["board_width"] == 8
    assert data["payload"]["board_height"] == 8
    assert data["payload"]["game_over"] is False
    

def test_snapshot_serializer_serializes_pieces():

    piece = PieceSnapshot(
        piece_id=1,
        kind=PieceKind.ROOK,
        color=Color.WHITE,
        position=Position(0, 0),
        state="idle",
    )

    snapshot = GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=[piece],
        selected_cell=None,
        legal_moves=set(),
        game_over=False,
    )

    result = SnapshotSerializer.serialize(snapshot)

    data = json.loads(result)

    serialized_piece = data["payload"]["pieces"][0]

    assert serialized_piece["piece_id"] == 1
    assert serialized_piece["kind"] == "ROOK"
    assert serialized_piece["color"] == "WHITE"
    assert serialized_piece["position"]["row"] == 0
    assert serialized_piece["position"]["col"] == 0
    assert serialized_piece["state"] == "idle"
