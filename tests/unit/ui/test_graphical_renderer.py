from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position
from kungfu_chess.ui.graphical_renderer import (
    GAME_OVER_TEXT,
    SELECTION_BORDER_COLOR,
    SELECTION_BORDER_THICKNESS,
    GraphicalRenderer,
)
from kungfu_chess.ui.promotion_picker_overlay import PromotionPickerOverlay
from kungfu_chess.view.game_snapshot import GameSnapshot, PieceSnapshot, PromotionSnapshot

CELL_SIZE = 100


class FakeStateProgressOverlay:
    def __init__(self):
        self.calls = []

    def draw(self, canvas, x, y, cell_size, progress):
        self.calls.append((canvas, x, y, cell_size, progress))


class FakePromotionPickerOverlay:
    def __init__(self):
        self.draw_calls = []

    def draw(self, canvas, promotion):
        self.draw_calls.append(promotion)


def make_renderer(background, provider=None, overlay=None, promotion_picker=None, board_offset=(0, 0)):
    if provider is None:
        provider = lambda piece: FakeImage()
    if overlay is None:
        overlay = FakeStateProgressOverlay()
    if promotion_picker is None:
        promotion_picker = FakePromotionPickerOverlay()

    return GraphicalRenderer(
        FakeSpriteLibrary(background),
        CELL_SIZE,
        provider,
        overlay,
        promotion_picker,
        board_offset,
    )


class FakeImage:
    def __init__(self):
        self.draw_on_calls = []
        self.put_text_calls = []
        self.draw_rect_calls = []

    def draw_on(self, other, x, y):
        self.draw_on_calls.append((other, x, y))

    def put_text(self, txt, x, y, font_size, color, thickness):
        self.put_text_calls.append((txt, x, y, font_size, color, thickness))

    def draw_rect(self, x, y, width, height, color, thickness):
        self.draw_rect_calls.append((x, y, width, height, color, thickness))


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


def make_snapshot(pieces, game_over=False, selected_cell=None, pending_promotion=None):
    return GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=pieces,
        selected_cell=selected_cell,
        legal_moves=set(),
        game_over=game_over,
        pending_promotion=pending_promotion,
    )


def test_renderer_uses_piece_state_from_snapshot():
    background = FakeImage()
    seen_states = []

    def provider(piece):
        seen_states.append(piece.state)
        return FakeImage()

    piece = PieceSnapshot(
        piece_id=1,
        kind=PieceKind.ROOK,
        color=Color.WHITE,
        position=Position(2, 3),
        state="long_rest",
        visual_position=(250.0, 350.0),
    )
    renderer = make_renderer(background, provider)

    renderer.render(make_snapshot([piece]))

    assert seen_states == ["long_rest"]


def test_render_returns_the_background_canvas():
    background = FakeImage()
    renderer = make_renderer(background)

    canvas = renderer.render(make_snapshot([]))

    assert canvas is background


def test_render_draws_provided_frame_at_pixel_position():
    background = FakeImage()
    frame = FakeImage()
    renderer = make_renderer(background, lambda piece: frame)

    piece = make_piece(row=2, col=3)

    renderer.render(make_snapshot([piece]))

    assert frame.draw_on_calls == [(background, 3 * CELL_SIZE, 2 * CELL_SIZE)]


def test_render_uses_frame_provider_per_piece():
    background = FakeImage()
    seen = []

    def provider(piece):
        seen.append(piece)
        return FakeImage()

    renderer = make_renderer(background, provider)

    pieces = [make_piece(0, 0), make_piece(1, 1)]
    renderer.render(make_snapshot(pieces))

    assert seen == pieces


def test_render_draws_game_over_overlay():
    background = FakeImage()
    renderer = make_renderer(background)

    renderer.render(make_snapshot([], game_over=True))

    assert len(background.put_text_calls) == 1
    assert background.put_text_calls[0][0] == GAME_OVER_TEXT


def test_render_skips_overlay_when_game_not_over():
    background = FakeImage()
    renderer = make_renderer(background)

    renderer.render(make_snapshot([], game_over=False))

    assert background.put_text_calls == []


def test_render_draws_selection_border_around_selected_cell():
    background = FakeImage()
    renderer = make_renderer(background)

    renderer.render(make_snapshot([], selected_cell=Position(2, 3)))

    assert background.draw_rect_calls == [
        (
            3 * CELL_SIZE,
            2 * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE,
            SELECTION_BORDER_COLOR,
            SELECTION_BORDER_THICKNESS,
        )
    ]


def test_render_skips_selection_when_no_selected_cell():
    background = FakeImage()
    renderer = make_renderer(background)

    renderer.render(make_snapshot([], selected_cell=None))

    assert background.draw_rect_calls == []


def test_render_draws_both_selection_and_game_over():
    background = FakeImage()
    renderer = make_renderer(background)

    renderer.render(
        make_snapshot([], game_over=True, selected_cell=Position(0, 0))
    )

    assert len(background.draw_rect_calls) == 1
    assert [call[0] for call in background.put_text_calls] == [GAME_OVER_TEXT]


def test_board_offset_shifts_piece_and_selection_positions():
    background = FakeImage()
    frame = FakeImage()
    offset = (40, 40)
    renderer = make_renderer(
        background,
        lambda piece: frame,
        board_offset=offset,
    )

    renderer.render(make_snapshot([make_piece(1, 2)], selected_cell=Position(1, 2)))

    expected_x = offset[0] + 2 * CELL_SIZE
    expected_y = offset[1] + 1 * CELL_SIZE
    assert frame.draw_on_calls == [(background, expected_x, expected_y)]
    assert background.draw_rect_calls[0][:2] == (expected_x, expected_y)


def test_render_skips_state_progress_overlay_when_progress_is_none():
    background = FakeImage()
    overlay = FakeStateProgressOverlay()
    renderer = make_renderer(background, overlay=overlay)

    renderer.render(make_snapshot([make_piece(0, 0)]))

    assert overlay.calls == []


def test_render_draws_state_progress_overlay_when_progress_is_set():
    background = FakeImage()
    overlay = FakeStateProgressOverlay()
    renderer = make_renderer(background, overlay=overlay)
    piece = PieceSnapshot(
        piece_id=1,
        kind=PieceKind.ROOK,
        color=Color.WHITE,
        position=Position(2, 3),
        state="any_state_name",
        state_progress=0.25,
    )

    renderer.render(make_snapshot([piece]))

    assert overlay.calls == [
        (background, 3 * CELL_SIZE, 2 * CELL_SIZE, CELL_SIZE, 0.25),
    ]


def test_state_progress_overlay_ignores_state_string():
    background = FakeImage()
    overlay = FakeStateProgressOverlay()
    renderer = make_renderer(background, overlay=overlay)
    pieces = [
        PieceSnapshot(
            piece_id=1,
            kind=PieceKind.ROOK,
            color=Color.WHITE,
            position=Position(0, 0),
            state="alpha",
            state_progress=0.0,
        ),
        PieceSnapshot(
            piece_id=2,
            kind=PieceKind.KING,
            color=Color.BLACK,
            position=Position(1, 1),
            state="beta",
            state_progress=0.0,
        ),
    ]

    renderer.render(make_snapshot(pieces))

    assert len(overlay.calls) == 2
    assert all(call[4] == 0.0 for call in overlay.calls)


def test_render_draws_promotion_picker_when_pending_promotion_exists():
    background = FakeImage()
    promotion_picker = FakePromotionPickerOverlay()
    renderer = make_renderer(background, promotion_picker=promotion_picker)
    promotion = PromotionSnapshot(
        piece_id=1,
        position=Position(0, 3),
        color=Color.WHITE,
        allowed_kinds=frozenset({PieceKind.QUEEN, PieceKind.KNIGHT}),
    )

    renderer.render(make_snapshot([], pending_promotion=promotion))

    assert promotion_picker.draw_calls == [promotion]


def test_render_skips_promotion_picker_when_no_pending_promotion():
    background = FakeImage()
    promotion_picker = FakePromotionPickerOverlay()
    renderer = make_renderer(background, promotion_picker=promotion_picker)

    renderer.render(make_snapshot([]))

    assert promotion_picker.draw_calls == []


def test_renderer_keeps_no_state_between_renders():
    renderer = make_renderer(FakeImage())

    attributes_before = set(vars(renderer))

    renderer.render(make_snapshot([make_piece(0, 0)]))
    renderer.render(make_snapshot([make_piece(1, 1)], game_over=True))

    assert set(vars(renderer)) == attributes_before
    assert set(vars(renderer)) == {
        "_sprite_library",
        "_cell_size",
        "_frame_provider",
        "_state_progress_overlay",
        "_promotion_picker_overlay",
        "_board_offset",
    }
