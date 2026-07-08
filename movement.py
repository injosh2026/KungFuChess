def handle_click(board, row, col, selected):
    if selected is None:
        if board[row][col] != ".":
            selected = (row, col)
    else:
        if board[row][col] != ".":
            selected = (row, col)
        else:
            board[row][col] = board[selected[0]][selected[1]]
            board[selected[0]][selected[1]] = "."
            selected = None
    return selected