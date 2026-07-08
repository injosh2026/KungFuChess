from constants import COORD_SCALE
from printer import print_board
from movement import handle_click
from game_clock import handle_wait
from game_state import GameState
from jump import handle_jump

def process_commands(lines, start_index, board):
    selected = None
    game_time = 0
    pending_moves = []
    pending_jumps = []
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
                
            if 0 <= row < len(board) and 0 <= col < len(board[0]):
                selected = handle_click(
                    board,
                    row,
                    col,
                    selected,
                    pending_moves,
                    game_time,
                    game_state
                )
                
        elif command[0] == "wait":
            ms = int(command[1])
            game_time = handle_wait(
                ms,
                game_time,
                board,
                pending_moves,
                pending_jumps,
                game_state
            )
            
        elif command[0] == "jump":
            x = int(command[1])
            y = int(command[2])
            
            col = x // COORD_SCALE
            row = y // COORD_SCALE
                
            if 0 <= row < len(board) and 0 <= col < len(board[0]):
                handle_jump(
                board,
                row,
                col,
                pending_jumps,
                pending_moves,
                game_time,
                game_state
            )
            
        elif command[0] == "print" and command[1] == "board":
            print_board(board) 
