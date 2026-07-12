import pytest

from kungfu_chess.view.renderer import Renderer


def test_renderer_requires_render_implementation():

    renderer = Renderer()

    with pytest.raises(NotImplementedError):
        renderer.render(None)