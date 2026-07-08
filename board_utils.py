
def is_path_clear(board, start, end):
    row_step = 1 if end[0] > start[0] else -1 if end[0] < start[0] else 0
    col_step = 1 if end[1] > start[1] else -1 if end[1] < start[1] else 0
    
    row = start[0] + row_step
    col = start[1] + col_step
    while (row, col) != end:
        if board[row][col] != ".":
            return False

        row += row_step
        col += col_step

    return True