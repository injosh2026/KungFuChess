from pieces import is_valid_move
from game_clock import calculate_move_time

def handle_click(board, row, col, selected, pending_moves, game_time):
    if selected is None:
        if board[row][col] != ".":
            if not is_piece_moving((row, col), pending_moves):
                selected = (row, col)
    else:
        piece = board[selected[0]][selected[1]]
        target = board[row][col]
        
        if target != ".":
            if same_color(piece, target):
                selected = (row, col)
            elif is_valid_move(board, piece, selected, (row, col)):
                move = {
                    "piece": piece,
                    "start": selected,
                    "end": (row, col),
                    "arrival": game_time + calculate_move_time(selected, (row, col))
                }

                pending_moves.append(move)
                selected = None
        else:
            if is_valid_move(board, piece, selected, (row, col)):
                move = {
                    "piece": piece,
                    "start": selected,
                    "end": (row, col),
                    "arrival": game_time + calculate_move_time(selected, (row, col))
                }

                pending_moves.append(move)
                selected = None
                
    return selected

def same_color(piece1, piece2):
    return piece1[0] == piece2[0]
    
def is_piece_moving(position, pending_moves):
    for move in pending_moves:
        if move["start"] == position:
            return True
    return False