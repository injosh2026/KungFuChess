from printer import print_board
from movement import handle_click
from game_clock import handle_wait

def process_commands(lines, start_index, board):
    selected = None
    game_time = 0
    pending_moves = []
    
    for line in lines[start_index:]:
        command = line.split()

        if not command:
            continue

        if command[0] == "click":
            x = int(command[1])
            y = int(command[2])

            col = x // 100
            row = y // 100
        
            if 0 <= row < len(board) and 0 <= col < len(board[0]):
                selected = handle_click(
                    board,
                    row,
                    col,
                    selected,
                    pending_moves,
                    game_time
                )
        
        elif command[0] == "wait":
            ms = int(command[1])
            game_time = handle_wait(ms, game_time, board, pending_moves)
        
        elif command[0] == "print" and command[1] == "board":
            print_board(board) 
