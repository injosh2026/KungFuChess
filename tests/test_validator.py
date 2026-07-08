import pytest

from validator import is_valid_token


@pytest.mark.parametrize(
    "token",
    [
        ".",
        "wK",
        "bK",
        "wQ",
        "bQ",
        "wR",
        "bR",
        "wB",
        "bB",
        "wN",
        "bN",
        "wP",
        "bP",
    ],
)
def test_is_valid_token_returns_true_for_valid_tokens(token):
    assert is_valid_token(token) is True


@pytest.mark.parametrize(
    "token",
    [
        "",
        "w",
        "wKK",
        " wK",
        "wK ",
        "xK",
        "WK",
        "bw",
        "wX",
        "wk",
        "..",
        "K",
        "b",
    ],
)
def test_is_valid_token_returns_false_for_invalid_tokens(token):
    assert is_valid_token(token) is False
