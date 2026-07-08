from constants import JUMP_DURATION_MS
from movement import is_piece_moving


def handle_jump(session, row, col):
    if session.game_over:
        return

    if session.board[row][col] == ".":
        return

    if is_piece_moving((row, col), session.pending_moves):
        return

    jump = {
        "piece": session.board[row][col],
        "position": (row, col),
        "end_time": session.game_time + JUMP_DURATION_MS,
    }

    session.pending_jumps.append(jump)
