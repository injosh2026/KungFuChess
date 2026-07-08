def handle_wait(ms, game_time, board, pending_moves, game_state):
    game_time += ms
    
    complete_moves(board, pending_moves, game_time, game_state)

    return game_time
 
    
def calculate_move_time(start, end):
    distance = max(
        abs(end[0] - start[0]),
        abs(end[1] - start[1])
    )

    return distance * 1000
 
    
def complete_moves(board, pending_moves, game_time, game_state):

    for move in pending_moves[:]:

        if move["arrival"] <= game_time:
            
            start_row, start_col = move["start"]
            end_row, end_col = move["end"]
            
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
            
            