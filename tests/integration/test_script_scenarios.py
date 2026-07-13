from kungfu_chess.texttests.script_runner import ScriptRunner


def test_script_prints_initial_board():

    runner = ScriptRunner()

    output = runner.run([
        "Board",
        "wK .",
        ". bK",
        "",
        "print board",
    ])

    assert output == [
        "wK .\n. bK"
    ]


def test_script_moves_rook_after_wait():

    runner = ScriptRunner()

    output = runner.run([
        "Board",
        "wR .",
        ". .",
        "",
        "click 50 50",
        "click 150 50",
        "wait 2000",
        "print board",
    ])

    assert output == [
        ". wR\n. ."
    ]