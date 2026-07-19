from typing import Callable

from img import Img


class MouseInput:
    """
    Translation layer between a window's mouse callback and a click handler.

    MouseInput forwards each click's pixel coordinates, unchanged, to the
    supplied handler (for example ``Controller.handle_click``). It registers
    with an ``Img`` window only after ``attach`` is called, once the window
    exists.

    It knows nothing about the game engine, game state, pieces, or the
    renderer. Its only responsibility is passing coordinates through.
    """

    def __init__(self, click_handler: Callable[[int, int], None]):
        self._click_handler = click_handler

    def attach(self, image: Img) -> None:
        image.set_click_handler(self._on_click)

    def _on_click(self, x: int, y: int) -> None:
        self._click_handler(x, y)
