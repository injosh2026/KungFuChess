from kungfu_chess.model.position import Position

RANKS_PER_SIDE = 8


def position_to_square(position: Position) -> str:
    """
    Converts a board position to algebraic square notation (e.g. e4).

    Row 0 is the top of the board (rank 8); row 7 is the bottom (rank 1).
    """
    file_letter = chr(ord("a") + position.col)
    rank_number = RANKS_PER_SIDE - position.row
    return f"{file_letter}{rank_number}"
