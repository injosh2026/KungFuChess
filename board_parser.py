from validator import is_valid_token

def parse_board(lines):
    board = []
    i = 1

    while lines[i] != "Commands:":
        board.append(lines[i].split())
        i += 1

    valid = validate_board(board)

    if not valid:
        return None, None
        
    return board, i
    

def validate_board(board):
    expected_width = len(board[0])

    for row in board:
        if len(row) != expected_width:
            print("ERROR ROW_WIDTH_MISMATCH")
            return False

        for token in row:
            if not is_valid_token(token):
                print("ERROR UNKNOWN_TOKEN")
                return False

    return True