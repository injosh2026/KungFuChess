import io
from unittest.mock import patch

from helpers import make_valid_stdin
from main import main


@patch("main.process_commands")
@patch("main.parse_board", return_value=(None, None))
def test_main_returns_early_when_board_is_invalid(
    mock_parse_board, mock_process_commands
):
    with patch("sys.stdin", io.StringIO("Board:\nwK .\nCommands:\n")):
        main()

    mock_parse_board.assert_called_once()
    mock_process_commands.assert_not_called()


@patch("main.process_commands")
@patch("main.parse_board")
def test_main_calls_process_commands_when_board_is_valid(
    mock_parse_board, mock_process_commands
):
    board = [["wK", "."]]
    mock_parse_board.return_value = (board, 2)

    with patch("sys.stdin", io.StringIO(make_valid_stdin())):
        main()

    mock_process_commands.assert_called_once()


@patch("main.process_commands")
@patch("main.parse_board")
def test_main_passes_correct_start_index_to_process_commands(
    mock_parse_board, mock_process_commands
):
    board = [["wK", "."]]
    lines = ["Board:", "wK .", "Commands:", "print board"]
    mock_parse_board.return_value = (board, 2)

    with patch("sys.stdin", io.StringIO("\n".join(lines))):
        main()

    mock_process_commands.assert_called_once_with(lines, 3, board)


@patch("main.parse_board", return_value=(None, None))
def test_main_reads_and_passes_lines_from_stdin(mock_parse_board):
    stdin_text = "\n\nBoard:\nwK .\nCommands:\nprint board\n\n"

    with patch("sys.stdin", io.StringIO(stdin_text)):
        main()

    called_lines = mock_parse_board.call_args[0][0]
    assert called_lines == ["Board:", "wK .", "Commands:", "print board"]


def test_main_integration_valid_input_runs_commands(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO(make_valid_stdin()))

    main()

    assert capsys.readouterr().out == "wK .\n"
