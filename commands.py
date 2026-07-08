from constants import COORD_SCALE
from printer import print_board
from movement import handle_click
from game_clock import handle_wait
from game_state import GameState
from game_session import create_session
from jump import handle_jump


def process_commands(lines, start_index, board):
    session = create_session(board)
    game_state = GameState()

    for line in lines[start_index:]:
        command = line.split()

        if not command:
            continue

        if command[0] == "click":
            x = int(command[1])
            y = int(command[2])

            col = x // COORD_SCALE
            row = y // COORD_SCALE

            if 0 <= row < len(session.board) and 0 <= col < len(session.board[0]):
                game_state.game_over = session.game_over
                session.selected = handle_click(
                    session.board,
                    row,
                    col,
                    session.selected,
                    session.pending_moves,
                    session.game_time,
                    game_state,
                )

        elif command[0] == "wait":
            ms = int(command[1])
            game_state.game_over = session.game_over
            session.game_time = handle_wait(
                ms,
                session.game_time,
                session.board,
                session.pending_moves,
                session.pending_jumps,
                game_state,
            )
            session.game_over = game_state.game_over

        elif command[0] == "jump":
            x = int(command[1])
            y = int(command[2])

            col = x // COORD_SCALE
            row = y // COORD_SCALE

            if 0 <= row < len(session.board) and 0 <= col < len(session.board[0]):
                game_state.game_over = session.game_over
                handle_jump(
                    session.board,
                    row,
                    col,
                    session.pending_jumps,
                    session.pending_moves,
                    session.game_time,
                    game_state,
                )

        elif command[0] == "print" and command[1] == "board":
            print_board(session.board)
