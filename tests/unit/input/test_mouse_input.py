from kungfu_chess.input.mouse_input import MouseInput


class FakeImg:
    def __init__(self):
        self.handler = None

    def set_click_handler(self, handler):
        self.handler = handler


def test_registers_handler_on_attach():
    image = FakeImg()
    mouse_input = MouseInput(lambda x, y: None)

    mouse_input.attach(image)

    assert image.handler is not None


def test_does_not_register_handler_before_attach():
    image = FakeImg()

    MouseInput(lambda x, y: None)

    assert image.handler is None


def test_forwards_click_coordinates_exactly():
    image = FakeImg()
    received = []
    mouse_input = MouseInput(lambda x, y: received.append((x, y)))

    mouse_input.attach(image)
    image.handler(37, 42)

    assert received == [(37, 42)]


def test_forwards_multiple_clicks_in_order():
    image = FakeImg()
    received = []
    mouse_input = MouseInput(lambda x, y: received.append((x, y)))

    mouse_input.attach(image)
    image.handler(0, 0)
    image.handler(100, 250)

    assert received == [(0, 0), (100, 250)]
