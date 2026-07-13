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


def test_script_valid_move_completes_after_wait():

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


def test_script_illegal_move_keeps_board_unchanged():

    runner = ScriptRunner()

    output = runner.run([
        "Board",
        "wR .",
        ". .",
        "",
        "click 50 50",
        "click 150 150",
        "wait 2000",
        "print board",
    ])

    assert output == [
        "wR .\n. ."
    ]


def test_script_blocked_move_keeps_board_unchanged():

    runner = ScriptRunner()

    output = runner.run([
        "Board",
        "wR wP .",
        ". . .",
        ". . .",
        "",
        "click 50 50",
        "click 250 50",
        "wait 2000",
        "print board",
    ])

    assert output == [
        "wR wP .\n. . .\n. . ."
    ]


def test_script_capture_removes_enemy_piece():

    runner = ScriptRunner()

    output = runner.run([
        "Board",
        "wR . bP",
        ". . .",
        ". . .",
        "",
        "click 50 50",
        "click 250 50",
        "wait 2000",
        "print board",
    ])

    assert output == [
        ". . wR\n. . .\n. . ."
    ]


def test_script_game_stops_after_king_capture():

    runner = ScriptRunner()

    output = runner.run([
        "Board",
        "wR . bK",
        ". . .",
        ". . .",
        "",
        "click 50 50",
        "click 250 50",
        "wait 2000",

        # ניסיון לבצע עוד מהלך לאחר סיום המשחק
        "click 250 50",
        "click 250 250",
        "wait 2000",

        "print board",
    ])

    assert output == [
        ". . wR\n. . .\n. . ."
    ]


def test_script_partial_movement_before_arrival():

    runner = ScriptRunner()

    output = runner.run([
        "Board",
        "wR . .",
        ". . .",
        ". . .",
        "",
        "click 50 50",
        "click 250 50",

        # עדיין לא הגיע
        "wait 500",
        "print board",

        # הגיע
        "wait 2000",
        "print board",
    ])

    assert output == [
        "wR . .\n. . .\n. . .",
        ". . wR\n. . .\n. . ."
    ]


def test_script_move_into_friendly_piece_keeps_board_unchanged():

    runner = ScriptRunner()

    output = runner.run([
        "Board",
        "wR .",
        ". wP",
        "",
        "click 50 50",
        "click 150 150",
        "wait 2000",
        "print board",
    ])

    assert output == [
        "wR .\n. wP"
    ]


def test_script_ignores_new_move_while_piece_is_moving():

    runner = ScriptRunner()

    output = runner.run([
        "Board",
        "wR . .",
        ". . .",
        ". . .",
        "",
        "click 50 50",
        "click 250 50",

        # הכלי עדיין בתנועה
        "wait 500",

        # ניסיון לבצע מהלך חדש בזמן תנועה
        "click 250 50",
        "click 250 250",

        # נותנים לתנועה הראשונה להסתיים
        "wait 2000",

        "print board",
    ])

    assert output == [
        ". . wR\n. . .\n. . ."
    ]