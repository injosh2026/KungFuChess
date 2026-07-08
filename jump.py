from constants import JUMP_DURATION_MS
from movement import is_piece_moving

def handle_jump(board, row, col, pending_jumps, pending_moves, game_time, game_state):
    if game_state.game_over:
        return
    
    if board[row][col] == ".":
        return

    if is_piece_moving((row,col), pending_moves):
        return

    jump = {
        "piece": board[row][col],
        "position": (row,col),
        "end_time": game_time + JUMP_DURATION_MS
    }

    pending_jumps.append(jump)