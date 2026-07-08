from pieces import is_valid_move

def handle_click(board, row, col, selected):
    if selected is None:
        if board[row][col] != ".":
            selected = (row, col)
    else:
        piece = board[selected[0]][selected[1]]
        target = board[row][col]
        
        if target != ".":
            if same_color(piece, target):
                selected = (row, col)
            elif is_valid_move(board, piece, selected, (row, col)):
                board[row][col] = piece
                board[selected[0]][selected[1]] = "."
                selected = None
        else:
            if is_valid_move(board, piece, selected, (row, col)):
                board[row][col] = piece
                board[selected[0]][selected[1]] = "."
                selected = None
                
    return selected

def same_color(piece1, piece2):
    return piece1[0] == piece2[0]