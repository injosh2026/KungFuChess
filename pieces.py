def is_valid_move(piece, start, end):

    piece_type = piece[1]

    row_diff = abs(end[0] - start[0])
    col_diff = abs(end[1] - start[1])
    
    if row_diff == 0 and col_diff == 0:
        return False
    
    if piece_type == "K":
        return king_move(row_diff, col_diff)

    if piece_type == "R":
        return rook_move(row_diff, col_diff)
        
    if piece_type == "B":
        return bishop_move(row_diff, col_diff)
        
    if piece_type == "Q":
        return queen_move(row_diff, col_diff)
        
    if piece_type == "N":
        return knight_move(row_diff, col_diff)
    
    return False
    
def king_move(row_diff, col_diff):
    return row_diff <= 1 and col_diff <= 1

def rook_move(row_diff, col_diff):
    return row_diff == 0 or col_diff == 0
    
def bishop_move(row_diff, col_diff):
    return row_diff == col_diff
    
def queen_move(row_diff, col_diff):
    return row_diff == col_diff or row_diff == 0 or col_diff == 0
    
def knight_move(row_diff, col_diff):
    return (
        (row_diff == 2 and col_diff == 1)
        or
        (row_diff == 1 and col_diff == 2)
    )