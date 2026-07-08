from constants import MOVE_DURATION_MS


def handle_wait(session, ms):
    session.game_time += ms
    complete_moves(session)
    complete_jumps(session)


def calculate_move_time(start, end):
    return MOVE_DURATION_MS


def complete_moves(session):
    for move in session.pending_moves[:]:
        if move["arrival"] <= session.game_time:
            start_row, start_col = move["start"]
            end_row, end_col = move["end"]

            jump = handle_airborne_collision(session, move)

            if jump:
                session.pending_jumps.remove(jump)
                session.pending_moves.remove(move)
                start_row, start_col = move["start"]
                session.board[start_row][start_col] = "."
                continue

            target = session.board[end_row][end_col]

            if target != "." and target[1] == "K":
                session.game_over = True

            session.board[start_row][start_col] = "."

            piece = move["piece"]

            if piece == "wP" and end_row == 0:
                piece = "wQ"

            if piece == "bP" and end_row == len(session.board) - 1:
                piece = "bQ"

            session.board[end_row][end_col] = piece

            session.pending_moves.remove(move)


def complete_jumps(session):
    for jump in session.pending_jumps[:]:
        if jump["end_time"] <= session.game_time:
            session.pending_jumps.remove(jump)


def handle_airborne_collision(session, move):
    for jump in session.pending_jumps:
        if jump["position"] == move["end"]:
            if jump["piece"][0] != move["piece"][0]:
                return jump

    return None
