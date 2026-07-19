PRESENT_WAIT_MS = 50


class GameApp:
    """
    Orchestrator for the game window loop.

    GameApp owns only the main loop and wires together already-built
    collaborators. It creates nothing, contains no game rules, does not
    handle clicks, and does not select sprites. Each iteration it advances
    simulation time, asks for a snapshot, renders it, and presents it.

    Time comes from a single free-running clock: the same clock feeds the
    animation frame selection (through the renderer's frame provider) and
    the per-iteration delta used to advance the engine, so animation and
    simulation stay consistent. The clock is never reset during a run.

    The mouse input is retained only to keep the window's click handler
    alive; GameApp never calls it. Clicks flow independently from the
    window callback into the controller.
    """

    def __init__(
        self,
        game_engine,
        controller,
        snapshot_builder,
        renderer,
        image,
        clock,
        mouse_input,
    ):
        self._game_engine = game_engine
        self._controller = controller
        self._snapshot_builder = snapshot_builder
        self._renderer = renderer
        self._image = image
        self._clock = clock
        self._mouse_input = mouse_input

    def run(self) -> None:
        self._image.open_window()
        self._image.prime_window()
        self._mouse_input.attach(self._image)

        last_elapsed_ms = self._clock.elapsed_ms()

        try:
            while True:
                now_ms = self._clock.elapsed_ms()
                delta_ms = now_ms - last_elapsed_ms
                last_elapsed_ms = now_ms

                self._game_engine.wait(delta_ms)

                snapshot = self._snapshot_builder.build(
                    self._game_engine.game_state,
                    self._controller.selected_position,
                    self._game_engine.active_motions(),
                    self._controller.legal_moves,
                )

                canvas = self._renderer.render(snapshot)
                canvas.present(PRESENT_WAIT_MS)
        except KeyboardInterrupt:
            pass
        finally:
            self._image.close()
