import copy

from printer import print_board


def test_print_board_prints_single_row(capsys):
    print_board([["wK", "."]])

    assert capsys.readouterr().out == "wK .\n"


def test_print_board_prints_multiple_rows(capsys):
    board = [["wK", "."], [".", "bP"]]

    print_board(board)

    assert capsys.readouterr().out == "wK .\n. bP\n"


def test_print_board_prints_empty_board_with_no_output(capsys):
    print_board([])

    assert capsys.readouterr().out == ""


def test_print_board_joins_tokens_with_spaces(capsys):
    print_board([["wQ"]])

    assert capsys.readouterr().out == "wQ\n"


def test_print_board_does_not_mutate_board(capsys):
    board = [["wK", "."], [".", "bP"]]
    expected = copy.deepcopy(board)

    print_board(board)

    assert board == expected
    capsys.readouterr()
