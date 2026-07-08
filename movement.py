from pieces import is_valid_move, get_route_type
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
                if can_start_move(piece, selected, (row, col), pending_moves):
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
                if can_start_move(piece, selected, (row, col), pending_moves):
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
    
def can_start_move(piece, start, end, pending_moves):
    route = get_route_type(start, end)

    for move in pending_moves:
        if move["piece"][0] != piece[0]:
            if get_route_type(move["start"], move["end"]) == route:
                return False

    return True