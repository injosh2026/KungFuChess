from kungfu_chess.model.game_session import create_session


def make_board(rows, cols, fill="."):    return [[fill for _ in range(cols)] for _ in range(rows)]


def make_move(piece, start, end, arrival=1000):
    return {
        "piece": piece,
        "start": start,
        "end": end,
        "arrival": arrival,
    }


def make_jump(piece, position, end_time=1000):
    return {
        "piece": piece,
        "position": position,
        "end_time": end_time,
    }


def make_session(    board,
    game_time=0,
    pending_moves=None,
    pending_jumps=None,
    selected=None,
    game_over=False,
):
    session = create_session(board)
    session.game_time = game_time
    session.pending_moves = pending_moves if pending_moves is not None else []
    session.pending_jumps = pending_jumps if pending_jumps is not None else []
    session.selected = selected
    session.game_over = game_over
    return session


def make_lines(board_rows, commands=None, header="Board:"):
    lines = [header, *board_rows, "Commands:"]
    if commands:
        lines.extend(commands)
    return lines


def make_valid_stdin(board_rows=None, commands=None):
    if board_rows is None:
        board_rows = ["wK ."]
    if commands is None:
        commands = ["print board"]
    return "\n".join(["Board:", *board_rows, "Commands:", *commands])
