from pathlib import Path

from kungfu_chess.model.piece_state import PieceState


ASSETS_ROOT = Path(__file__).resolve().parent.parents[1] / "assets"
PIECE_SET = "pieces2"
BOARD_FILENAME = "board.png"
CELL_SIZE = 100
PRESENT_WAIT_MS = 50

ASSET_STATE_BY_PIECE_STATE = {
    PieceState.IDLE: "idle",
    PieceState.MOVING: "move",
}

STARTING_BOARD = [
    "bR bN bB bQ bK bB bN bR",
    "bP bP bP bP bP bP bP bP",
    ".  .  .  .  .  .  .  .",
    ".  .  .  .  .  .  .  .",
    ".  .  .  .  .  .  .  .",
    ".  .  .  .  .  .  .  .",
    "wP wP wP wP wP wP wP wP",
    "wR wN wB wQ wK wB wN wR",
]