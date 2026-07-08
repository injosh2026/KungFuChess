from pieces import is_valid_move

def handle_click(board, row, col, selected):
    if selected is None:
        if board[row][col] != ".":
            selected = (row, col)
    else:
        if board[row][col] != ".":
            selected = (row, col)
        else:
            piece = board[selected[0]][selected[1]]
            if is_valid_move(piece, selected, (row, col)):
                board[row][col] = piece
                board[selected[0]][selected[1]] = "."
            selected = None
    return selected
