from __future__ import annotations

import pathlib
from typing import Callable

import cv2
import numpy as np

DEFAULT_WINDOW_TITLE = "KungFuChess"


class Cv2Window:
    """
    OpenCV-backed window layer.

    Keeps every OpenCV GUI call in one place, so the window/event handling
    is isolated behind a small interface that can be replaced in tests.
    """

    def create(self, title: str) -> None:
        cv2.namedWindow(title)

    def show(self, title: str, image) -> None:
        cv2.imshow(title, image)

    def pump(self, wait_ms: int) -> None:
        cv2.waitKey(wait_ms)

    def set_click_handler(
        self, title: str, handler: Callable[[int, int], None]
    ) -> None:
        def on_mouse(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                handler(x, y)

        cv2.setMouseCallback(title, on_mouse)

    def destroy(self, title: str) -> None:
        cv2.destroyWindow(title)


class Img:
    def __init__(self, window=None):
        self.img = None
        self._window = window if window is not None else Cv2Window()
        self._title = DEFAULT_WINDOW_TITLE

    def read(
        self,
        path: str | pathlib.Path,
        size: tuple[int, int] | None = None,
        keep_aspect: bool = False,
        interpolation: int = cv2.INTER_AREA,
    ) -> "Img":
        """
        Load `path` into self.img and **optionally resize**.

        Parameters
        ----------
        path : str | Path
            Image file to load.
        size : (width, height) | None
            Target size in pixels.  If None, keep original.
        keep_aspect : bool
            • False  → resize exactly to `size`
            • True   → shrink so the *longer* side fits `size` while
                       preserving aspect ratio (no cropping).
        interpolation : OpenCV flag
            E.g.  `cv2.INTER_AREA` for shrink, `cv2.INTER_LINEAR` for enlarge.

        Returns
        -------
        Img
            `self`, so you can chain:  `sprite = Img().read("foo.png", (64,64))`
        """
        path = str(path)
        self.img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if self.img is None:
            raise FileNotFoundError(f"Cannot load image: {path}")

        if size is not None:
            target_w, target_h = size
            h, w = self.img.shape[:2]

            if keep_aspect:
                scale = min(target_w / w, target_h / h)
                new_w, new_h = int(w * scale), int(h * scale)
            else:
                new_w, new_h = target_w, target_h

            self.img = cv2.resize(self.img, (new_w, new_h), interpolation=interpolation)

        return self

    def draw_on(self, other_img, x, y):
        if self.img is None or other_img.img is None:
            raise ValueError("Both images must be loaded before drawing.")

        if self.img.shape[2] != other_img.img.shape[2]:
            if self.img.shape[2] == 3 and other_img.img.shape[2] == 4:
                self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2BGRA)
            elif self.img.shape[2] == 4 and other_img.img.shape[2] == 3:
                self.img = cv2.cvtColor(self.img, cv2.COLOR_BGRA2BGR)

        h, w = self.img.shape[:2]
        H, W = other_img.img.shape[:2]

        if y + h > H or x + w > W:
            raise ValueError("Logo does not fit at the specified position.")

        roi = other_img.img[y : y + h, x : x + w]

        if self.img.shape[2] == 4:
            b, g, r, a = cv2.split(self.img)
            mask = a / 255.0
            for c in range(3):
                roi[..., c] = (1 - mask) * roi[..., c] + mask * self.img[..., c]
        else:
            other_img.img[y : y + h, x : x + w] = self.img

    def put_text(self, txt, x, y, font_size, color=(255, 255, 255, 255), thickness=1):
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.putText(
            self.img,
            txt,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_size,
            color,
            thickness,
            cv2.LINE_AA,
        )

    def show(self):
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.imshow("Image", self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def open_window(self, title: str = DEFAULT_WINDOW_TITLE) -> None:
        self._title = title
        self._window.create(title)

    def present(self, wait_ms: int = 1) -> None:
        if self.img is None:
            raise ValueError("Image not loaded.")
        self._window.show(self._title, self.img)
        self._window.pump(wait_ms)

    def set_click_handler(self, handler: Callable[[int, int], None]) -> None:
        self._window.set_click_handler(self._title, handler)

    def close(self) -> None:
        self._window.destroy(self._title)

    def create_blank(self, width, height, color=(0, 0, 0, 255)) -> "Img":
        self.img = np.zeros((height, width, len(color)), dtype=np.uint8)
        self.img[:] = color
        return self

    def draw_rect(
        self, x, y, width, height, color=(0, 255, 255, 255), thickness=3
    ) -> None:
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.rectangle(self.img, (x, y), (x + width, y + height), color, thickness)

    def tint_rect(
        self,
        x,
        y,
        width,
        height,
        color=(0, 255, 255),
        alpha=0.25,
    ):
        if self.img is None:
            raise ValueError("Image not loaded.")

        cell = self.img[y : y + height, x : x + width]

        rgb = np.array(color)

        cell[..., :3] = (cell[..., :3] * (1 - alpha) + rgb * alpha).astype("uint8")
