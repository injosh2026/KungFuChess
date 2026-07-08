def handle_wait(ms, game_time, board, pending_moves):
    game_time += ms
    
    complete_moves(board, pending_moves, game_time)

    return game_time
 
    
def calculate_move_time(start, end):
    distance = abs(end[0] - start[0]) + abs(end[1] - start[1])

    return distance * 1000
 
    
def complete_moves(board, pending_moves, game_time):

    for move in pending_moves[:]:

        if move["arrival"] <= game_time:
            
            start_row, start_col = move["start"]
            end_row, end_col = move["end"]
            
            board[start_row][start_col] = "."
            board[end_row][end_col] = move["piece"]
            
            pending_moves.remove(move)