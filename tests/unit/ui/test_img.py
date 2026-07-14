from img import DEFAULT_WINDOW_TITLE, Img

FRAME = "frame-array"
TITLE = "TestWindow"


class FakeWindow:
    def __init__(self):
        self.created = []
        self.shown = []
        self.pumped = []
        self.click_handlers = []
        self.destroyed = []

    def create(self, title):
        self.created.append(title)

    def show(self, title, image):
        self.shown.append((title, image))

    def pump(self, wait_ms):
        self.pumped.append(wait_ms)

    def set_click_handler(self, title, handler):
        self.click_handlers.append((title, handler))

    def destroy(self, title):
        self.destroyed.append(title)


def make_img():
    window = FakeWindow()
    return Img(window=window), window


def test_open_window_creates_named_window():
    img, window = make_img()

    img.open_window(TITLE)

    assert window.created == [TITLE]


def test_open_window_uses_default_title():
    img, window = make_img()

    img.open_window()

    assert window.created == [DEFAULT_WINDOW_TITLE]


def test_present_shows_frame_and_pumps_events():
    img, window = make_img()
    img.img = FRAME
    img.open_window(TITLE)

    img.present(5)

    assert window.shown == [(TITLE, FRAME)]
    assert window.pumped == [5]


def test_present_returns_none():
    img, _ = make_img()
    img.img = FRAME

    assert img.present() is None


def test_present_without_image_raises():
    img, _ = make_img()

    try:
        img.present()
    except ValueError:
        return

    raise AssertionError("present should raise when no image is loaded")


def test_set_click_handler_registers_handler():
    img, window = make_img()
    img.open_window(TITLE)

    received = []

    def handler(x, y):
        received.append((x, y))

    img.set_click_handler(handler)

    assert len(window.click_handlers) == 1
    title, registered = window.click_handlers[0]
    assert title == TITLE

    registered(3, 4)
    assert received == [(3, 4)]


def test_close_destroys_window():
    img, window = make_img()
    img.open_window(TITLE)

    img.close()

    assert window.destroyed == [TITLE]
