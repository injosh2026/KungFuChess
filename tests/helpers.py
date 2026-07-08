from game_state import GameState


def make_board(rows, cols, fill="."):
    return [[fill for _ in range(cols)] for _ in range(rows)]


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


def make_game_state(game_over=False):
    game_state = GameState()
    game_state.game_over = game_over
    return game_state


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
