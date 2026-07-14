from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position
from kungfu_chess.ui.graphical_renderer import GAME_OVER_TEXT, GraphicalRenderer
from kungfu_chess.view.game_snapshot import GameSnapshot, PieceSnapshot

CELL_SIZE = 100


class FakeImage:
    def __init__(self):
        self.draw_on_calls = []
        self.put_text_calls = []

    def draw_on(self, other, x, y):
        self.draw_on_calls.append((other, x, y))

    def put_text(self, txt, x, y, font_size, color, thickness):
        self.put_text_calls.append((txt, x, y, font_size, color, thickness))


class FakeSpriteLibrary:
    def __init__(self, background):
        self._background = background

    def background(self):
        return self._background


def make_piece(row, col):
    return PieceSnapshot(
        piece_id=1,
        kind=PieceKind.ROOK,
        color=Color.WHITE,
        position=Position(row, col),
        state=PieceState.IDLE,
    )


def make_snapshot(pieces, game_over=False):
    return GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=pieces,
        selected_cell=None,
        game_over=game_over,
    )


def test_render_returns_the_background_canvas():
    background = FakeImage()
    renderer = GraphicalRenderer(
        FakeSpriteLibrary(background), CELL_SIZE, lambda piece: FakeImage()
    )

    canvas = renderer.render(make_snapshot([]))

    assert canvas is background


def test_render_draws_provided_frame_at_pixel_position():
    background = FakeImage()
    frame = FakeImage()
    renderer = GraphicalRenderer(
        FakeSpriteLibrary(background), CELL_SIZE, lambda piece: frame
    )

    piece = make_piece(row=2, col=3)

    renderer.render(make_snapshot([piece]))

    assert frame.draw_on_calls == [(background, 3 * CELL_SIZE, 2 * CELL_SIZE)]


def test_render_uses_frame_provider_per_piece():
    background = FakeImage()
    seen = []

    def provider(piece):
        seen.append(piece)
        return FakeImage()

    renderer = GraphicalRenderer(FakeSpriteLibrary(background), CELL_SIZE, provider)

    pieces = [make_piece(0, 0), make_piece(1, 1)]
    renderer.render(make_snapshot(pieces))

    assert seen == pieces


def test_render_draws_game_over_overlay():
    background = FakeImage()
    renderer = GraphicalRenderer(
        FakeSpriteLibrary(background), CELL_SIZE, lambda piece: FakeImage()
    )

    renderer.render(make_snapshot([], game_over=True))

    assert len(background.put_text_calls) == 1
    assert background.put_text_calls[0][0] == GAME_OVER_TEXT


def test_render_skips_overlay_when_game_not_over():
    background = FakeImage()
    renderer = GraphicalRenderer(
        FakeSpriteLibrary(background), CELL_SIZE, lambda piece: FakeImage()
    )

    renderer.render(make_snapshot([], game_over=False))

    assert background.put_text_calls == []


def test_renderer_keeps_no_state_between_renders():
    renderer = GraphicalRenderer(
        FakeSpriteLibrary(FakeImage()), CELL_SIZE, lambda piece: FakeImage()
    )

    attributes_before = set(vars(renderer))

    renderer.render(make_snapshot([make_piece(0, 0)]))
    renderer.render(make_snapshot([make_piece(1, 1)], game_over=True))

    assert set(vars(renderer)) == attributes_before
    assert set(vars(renderer)) == {
        "_sprite_library",
        "_cell_size",
        "_frame_provider",
    }
