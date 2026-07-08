from constants import COORD_SCALE
from printer import print_board
from movement import handle_click
from game_clock import handle_wait
from game_session import create_session
from jump import handle_jump


def process_commands(lines, start_index, board):
    session = create_session(board)

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
                handle_click(session, row, col)

        elif command[0] == "wait":
            ms = int(command[1])
            handle_wait(session, ms)

        elif command[0] == "jump":
            x = int(command[1])
            y = int(command[2])

            col = x // COORD_SCALE
            row = y // COORD_SCALE

            if 0 <= row < len(session.board) and 0 <= col < len(session.board[0]):
                handle_jump(session, row, col)

        elif command[0] == "print" and command[1] == "board":
            print_board(session.board)
