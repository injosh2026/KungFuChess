import pytest

from kungfu_chess.view.renderer import Renderer


def test_renderer_requires_render_implementation():

    with pytest.raises(TypeError):
        Renderer()
