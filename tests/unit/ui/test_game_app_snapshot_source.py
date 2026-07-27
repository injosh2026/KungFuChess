from kungfu_chess.ui.game_app import GameApp


def test_game_app_exposes_snapshot_source():

    snapshot_source = object()

    app = GameApp(
        game_engine=object(),
        controller=object(),
        snapshot_source=snapshot_source,
        renderer=object(),
        image=object(),
        clock=object(),
        mouse_input=object(),
    )

    assert app.snapshot_source is snapshot_source