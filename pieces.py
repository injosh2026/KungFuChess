from piece_moves import (
    king_move,
    rook_move,
    bishop_move,
    queen_move,
    knight_move,
    pawn_move
)

def is_valid_move(board,  piece, start, end):
    piece_type = piece[1]

    row_diff = abs(end[0] - start[0])
    col_diff = abs(end[1] - start[1])
    
    if row_diff == 0 and col_diff == 0:
        return False
    
    if piece_type == "K":
        return king_move(row_diff, col_diff) 

    if piece_type == "R":
        return rook_move(board, row_diff, col_diff, start, end)
        
    if piece_type == "B":
        return bishop_move(board, row_diff, col_diff, start, end)
        
    if piece_type == "Q":
        return queen_move(board, row_diff, col_diff, start, end)
        
    if piece_type == "N":
        return knight_move(row_diff, col_diff)
    
    if piece_type == "P":
        return pawn_move(board, piece, start, end)
    
    return False

def get_route_type(start, end):
    row_diff = abs(end[0] - start[0])
    col_diff = abs(end[1] - start[1])

    if row_diff == 0:
        return "horizontal"

    if col_diff == 0:
        return "vertical"

    return "diagonal"
    
