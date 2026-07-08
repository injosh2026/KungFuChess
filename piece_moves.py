from board_utils import is_path_clear

def king_move(row_diff, col_diff):
    return row_diff <= 1 and col_diff <= 1

def rook_move(board, row_diff, col_diff, start, end):
    return (row_diff == 0 or col_diff == 0) and is_path_clear(board, start, end)
    
def bishop_move(board, row_diff, col_diff, start, end):
    return row_diff == col_diff and is_path_clear(board, start, end)
    
def queen_move(board, row_diff, col_diff, start, end):
    return (row_diff == col_diff or row_diff == 0 or col_diff == 0) and is_path_clear(board, start, end)
    
def knight_move(row_diff, col_diff):
    return (
        (row_diff == 2 and col_diff == 1)
        or
        (row_diff == 1 and col_diff == 2)
    )
    
def pawn_move(board, piece, start, end):
    direction = -1 if piece[0] == "w" else 1

    row_diff = end[0] - start[0]
    col_diff = abs(end[1] - start[1])

    if col_diff == 0:
        return row_diff == direction and board[end[0]][end[1]] == "."
      
    if col_diff == 1 and row_diff == direction:
        return (
            board[end[0]][end[1]] != "."
            and board[end[0]][end[1]][0] != piece[0]
        )  
    return False
    
    