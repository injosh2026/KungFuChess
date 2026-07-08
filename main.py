import sys
from board_parser import parse_board
from printer import print_board
from commands import process_commands

def main():
    text_input = sys.stdin.read()
    lines = text_input.strip().splitlines()
    
    board, command_index = parse_board(lines)
    
    if board is None:
        return
    
    process_commands(lines, command_index + 1, board)          
                
if __name__ == "__main__":
    main()