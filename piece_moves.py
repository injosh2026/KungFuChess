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