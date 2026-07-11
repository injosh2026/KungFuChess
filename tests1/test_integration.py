import io

from board_parser import parse_board
from commands import process_commands
from helpers import make_lines, make_valid_stdin
from main import main


def test_integration_parse_and_run_click_wait_print(capsys):
    lines = make_lines(
        ["wK . . .", ". . . .", ". . . .", ". . . ."],
        ["click 0 0", "click 100 0", "wait 1000", "print board"],
    )
    board, command_index = parse_board(lines)

    assert board is not None
    process_commands(lines, command_index + 1, board)

    assert board[0][0] == "."
    assert board[0][1] == "wK"
    assert ". wK" in capsys.readouterr().out


def test_integration_rook_captures_king():
    lines = make_lines(
        ["wR bK . .", ". . . .", ". . . .", ". . . ."],
        ["click 0 0", "click 100 0", "wait 1000"],
    )
    board, command_index = parse_board(lines)

    process_commands(lines, command_index + 1, board)

    assert board[0][0] == "."
    assert board[0][1] == "wR"


def test_integration_white_pawn_promotion():
    lines = make_lines(
        [". . . .", "wP . . .", ". . . .", ". . . ."],
        ["click 0 100", "click 0 0", "wait 1000"],
    )
    board, command_index = parse_board(lines)

    process_commands(lines, command_index + 1, board)

    assert board[1][0] == "."
    assert board[0][0] == "wQ"


def test_integration_airborne_collision_prevents_landing():
    lines = make_lines(
        ["wR bN . .", ". . . .", ". . . .", ". . . ."],
        [
            "jump 100 0",
            "click 0 0",
            "click 100 0",
            "wait 1000",
        ],
    )
    board, command_index = parse_board(lines)

    process_commands(lines, command_index + 1, board)

    assert board[0][0] == "."
    assert board[0][1] == "bN"


def test_integration_main_end_to_end_with_valid_input(capsys, monkeypatch):
    monkeypatch.setattr(
        "sys.stdin",
        io.StringIO(make_valid_stdin(["wK ."], ["print board"])),
    )

    main()

    assert capsys.readouterr().out == "wK .\n"
