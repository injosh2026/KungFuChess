from pieces import is_valid_move, get_route_type
from game_clock import calculate_move_time


def _schedule_move(session, piece, start, end):
    move = {
        "piece": piece,
        "start": start,
        "end": end,
        "arrival": session.game_time + calculate_move_time(start, end),
    }
    if can_start_move(piece, start, end, session.pending_moves):
        session.pending_moves.append(move)
        session.selected = None


def handle_click(session, row, col):
    if session.game_over:
        return

    if session.selected is None:
        if session.board[row][col] != ".":
            if not is_piece_moving((row, col), session.pending_moves):
                session.selected = (row, col)
    else:
        piece = session.board[session.selected[0]][session.selected[1]]
        target = session.board[row][col]
        if target != "." and same_color(piece, target):
            session.selected = (row, col)
        elif is_valid_move(session.board, piece, session.selected, (row, col)):
            _schedule_move(session, piece, session.selected, (row, col))


def same_color(piece1, piece2):
    return piece1[0] == piece2[0]


def is_piece_moving(position, pending_moves):
    for move in pending_moves:
        if move["start"] == position:
            return True
    return False


def can_start_move(piece, start, end, pending_moves):
    route = get_route_type(start, end)

    for move in pending_moves:
        if move["piece"][0] != piece[0]:
            if get_route_type(move["start"], move["end"]) == route:
                return False

    return True
