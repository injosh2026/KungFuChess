import sys
from board_parser import parse_board
from printer import print_board

def main():
    text_input = sys.stdin.read()
    lines = text_input.strip().splitlines()
    
    board, command_index = parse_board(lines)
    
    if command_index + 1 < len(lines):       
        if lines[command_index + 1] == "print board":
            print_board(board) 
                
                
if __name__ == "__main__":
    main()