from constants import MOVE_DURATION_MS


def handle_wait(ms, game_time, board, pending_moves, pending_jumps, game_state):
    game_time += ms
    
    complete_moves(board, pending_moves, pending_jumps, game_time, game_state)
    complete_jumps(board, pending_jumps, game_time)
    
    return game_time
 
    
def calculate_move_time(start, end):
    return MOVE_DURATION_MS
 
    
def complete_moves(board, pending_moves, pending_jumps, game_time, game_state):

    for move in pending_moves[:]:

        if move["arrival"] <= game_time:
            
            start_row, start_col = move["start"]
            end_row, end_col = move["end"]
            
            jump = handle_airborne_collision(board, move, pending_jumps)
            
            if jump:
                pending_jumps.remove(jump)
                pending_moves.remove(move)
                start_row, start_col = move["start"]
                board[start_row][start_col] = "."
                continue
            
            target = board[end_row][end_col]
            
            if target != "." and target[1] == "K":
                game_state.game_over = True
            
            board[start_row][start_col] = "."
            
            piece = move["piece"]
            
            if piece == "wP" and end_row == 0:
                piece = "wQ"
            
            if piece == "bP" and end_row == len(board) - 1:
                piece = "bQ"
            
            board[end_row][end_col] = piece
            
            pending_moves.remove(move)
         
           
def complete_jumps(board, pending_jumps, game_time):
    for jump in pending_jumps[:]:
        
        if jump["end_time"] <= game_time:
            
            pending_jumps.remove(jump)


def handle_airborne_collision(board, move, pending_jumps):
    for jump in pending_jumps:
        if jump["position"] == move["end"]:
            if jump["piece"][0] != move["piece"][0]:
                return jump

    return None  
            