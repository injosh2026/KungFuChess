from board_utils import is_path_clear


def king_move(row_diff, col_diff):
    return row_diff <= 1 and col_diff <= 1


def rook_move(board, row_diff, col_diff, start, end):
    return (row_diff == 0 or col_diff == 0) and is_path_clear(board, start, end)


def bishop_move(board, row_diff, col_diff, start, end):
    return row_diff == col_diff and is_path_clear(board, start, end)


def queen_move(board, row_diff, col_diff, start, end):
    return (row_diff == col_diff or row_diff == 0 or col_diff == 0) and is_path_clear(
        board, start, end
    )


def knight_move(row_diff, col_diff):
    return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)


def pawn_move(board, piece, start, end):
    direction = -1 if piece[0] == "w" else 1

    row_diff = end[0] - start[0]
    col_diff = abs(end[1] - start[1])

    if row_diff == direction and col_diff == 0:
        return board[end[0]][end[1]] == "."

    if row_diff == 2 * direction and col_diff == 0:
        if not is_pawn_start_row(piece, start):
            return False

        middle_row = start[0] + direction

        return board[middle_row][start[1]] == "." and board[end[0]][start[1]] == "."

    if row_diff == direction and col_diff == 1:
        return board[end[0]][end[1]] != "."

    return False


def is_pawn_start_row(piece, start):
    if piece[0] == "w":
        return start[0] == 3

    return start[0] == 0
