from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.model.position import Position
from kungfu_chess.ui.board_coordinates_renderer import BoardCoordinatesRenderer
from kungfu_chess.ui.player_panel import PlayerPanel
from kungfu_chess.ui.player_panel_data import PlayerPanelConfig, PlayerPanelData
from kungfu_chess.ui.game_ui_layout import BOOTSTRAP_VIEWPORT
from kungfu_chess.ui.graphical_renderer import (
    GAME_OVER_TEXT,
    SELECTION_BORDER_COLOR,
    SELECTION_BORDER_THICKNESS,
    GraphicalRenderer,
)
from kungfu_chess.ui.game_ui_layout import GameUILayout
from kungfu_chess.view.game_snapshot import GameSnapshot, PieceSnapshot, PromotionSnapshot
from kungfu_chess.view.move_history_entry import MoveHistoryEntry
from kungfu_chess.view.runtime_role import RuntimeRole
import numpy as np

CELL_SIZE = 100


def chrome_free_canvas_size(width=800, height=800):
    return GameUILayout.from_canvas_size(
        width,
        height,
        header_ratio=0.0,
        footer_ratio=0.0,
        sidebar_ratio=0.0,
    ).canvas_size


def default_canvas_size():
    return chrome_free_canvas_size()


def layout_with_board_offset(offset_x: int, offset_y: int, board_side: int = 800):
    return GameUILayout.from_canvas_size(
        board_side + 2 * offset_x,
        board_side + 2 * offset_y,
        header_ratio=0.0,
        footer_ratio=0.0,
        sidebar_ratio=0.0,
    )


class FakeStateProgressOverlay:
    def __init__(self):
        self.calls = []

    def draw(self, canvas, x, y, cell_size, progress):
        self.calls.append((canvas, x, y, cell_size, progress))


class FakePromotionPickerOverlay:
    def __init__(self):
        self.draw_calls = []

    def draw(self, canvas, promotion, canvas_width, canvas_height):
        self.draw_calls.append(promotion)


class FakeMoveHistoryPanel:
    def __init__(self):
        self.draw_calls = []

    def draw(self, canvas, move_history, bounds):
        self.draw_calls.append((canvas, move_history, bounds))


class FakePlayerPanel:
    def __init__(self):
        self.draw_calls = []

    def draw(self, canvas, data, bounds):
        self.draw_calls.append((canvas, data, bounds))


DEFAULT_LEFT_PLAYER = PlayerPanelConfig("White", "W")
DEFAULT_RIGHT_PLAYER = PlayerPanelConfig("Black", "B")


def make_renderer(
    background,
    provider=None,
    overlay=None,
    promotion_picker=None,
    white_history_panel=None,
    black_history_panel=None,
    canvas_size=None,
    board_coordinates_renderer=None,
    player_panel=None,
    left_player_panel_data=DEFAULT_LEFT_PLAYER,
    right_player_panel_data=DEFAULT_RIGHT_PLAYER,
):
    if provider is None:
        provider = lambda piece: FakeImage()
    if overlay is None:
        overlay = FakeStateProgressOverlay()
    if promotion_picker is None:
        promotion_picker = FakePromotionPickerOverlay()
    if white_history_panel is None:
        white_history_panel = FakeMoveHistoryPanel()
    if black_history_panel is None:
        black_history_panel = FakeMoveHistoryPanel()
    if board_coordinates_renderer is None:
        board_coordinates_renderer = BoardCoordinatesRenderer()
    if player_panel is None:
        player_panel = FakePlayerPanel()
    if canvas_size is None:
        canvas_size_provider = default_canvas_size
    elif callable(canvas_size):
        canvas_size_provider = canvas_size
    else:
        canvas_size_provider = lambda: canvas_size

    return GraphicalRenderer(
        FakeSpriteLibrary(background),
        canvas_size_provider,
        provider,
        overlay,
        promotion_picker,
        white_history_panel,
        black_history_panel,
        board_coordinates_renderer,
        player_panel,
        left_player_panel_data,
        right_player_panel_data,
    )


class FakeImage:
    def __init__(self, width=CELL_SIZE, height=CELL_SIZE):
        self.draw_on_calls = []
        self.put_text_calls = []
        self.draw_rect_calls = []
        self.img = np.zeros((height, width, 4), dtype=np.uint8)

    def draw_on(self, other, x, y):
        self.draw_on_calls.append((other, x, y))

    def put_text(self, txt, x, y, font_size, color, thickness):
        self.put_text_calls.append((txt, x, y, font_size, color, thickness))

    def draw_rect(self, x, y, width, height, color, thickness):
        self.draw_rect_calls.append((x, y, width, height, color, thickness))


class FakeSpriteLibrary:
    def __init__(self, background):
        self._background = background
        self.last_board_origin = None
        self.last_canvas_size = None

    def set_display_cell_size(self, cell_size):
        pass

    def background(self, canvas_width, canvas_height, board_origin=None):
        self.last_board_origin = board_origin
        self.last_canvas_size = (canvas_width, canvas_height)
        return self._background


def make_piece(row, col):
    return PieceSnapshot(
        piece_id=1,
        kind=PieceKind.ROOK,
        color=Color.WHITE,
        position=Position(row, col),
        state=PieceState.IDLE,
    )


def make_snapshot(
    pieces,
    game_over=False,
    selected_cell=None,
    pending_promotion=None,
    move_history=(),
    player_scores=None,
):
    if player_scores is None:
        player_scores = {}
    return GameSnapshot(
        board_width=8,
        board_height=8,
        pieces=pieces,
        selected_cell=selected_cell,
        legal_moves=set(),
        game_over=game_over,
        pending_promotion=pending_promotion,
        move_history=move_history,
        player_scores=player_scores,
    )


def test_render_displays_player_scores_from_snapshot():
    background = FakeImage()
    renderer = make_renderer(background, player_panel=PlayerPanel())

    renderer.render(make_snapshot([], player_scores={"W": 7, "B": 2}))

    score_lines = [
        call[0]
        for call in background.put_text_calls
        if call[0].startswith("Score:")
    ]
    assert score_lines == ["Score: 7", "Score: 2"]


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

    layout = renderer.layout
    expected_x = layout.board_offset[0] + 3 * layout.display_cell_size
    expected_y = layout.board_offset[1] + 2 * layout.display_cell_size
    assert frame.draw_on_calls == [(background, expected_x, expected_y)]


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

    game_over_calls = [
        call for call in background.put_text_calls if call[0] == GAME_OVER_TEXT
    ]
    assert len(game_over_calls) == 1


def test_render_skips_overlay_when_game_not_over():
    background = FakeImage()
    renderer = make_renderer(background)

    renderer.render(make_snapshot([], game_over=False))

    assert GAME_OVER_TEXT not in [call[0] for call in background.put_text_calls]


def test_render_draws_selection_border_around_selected_cell():
    background = FakeImage()
    renderer = make_renderer(background)

    renderer.render(make_snapshot([], selected_cell=Position(2, 3)))

    layout = renderer.layout
    expected_x = layout.board_offset[0] + 3 * layout.display_cell_size
    expected_y = layout.board_offset[1] + 2 * layout.display_cell_size
    assert background.draw_rect_calls == [
        (
            expected_x,
            expected_y,
            layout.display_cell_size,
            layout.display_cell_size,
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
    assert [call[0] for call in background.put_text_calls if call[0] == GAME_OVER_TEXT] == [
        GAME_OVER_TEXT
    ]


def test_board_offset_shifts_piece_and_selection_positions():
    background = FakeImage()
    frame = FakeImage()
    canvas_size = (1000, 800)
    layout = GameUILayout.from_canvas_size(*canvas_size)
    renderer = make_renderer(
        background,
        lambda piece: frame,
        canvas_size=canvas_size,
    )

    renderer.render(make_snapshot([make_piece(1, 2)], selected_cell=Position(1, 2)))

    expected_x = layout.board_offset[0] + 2 * layout.display_cell_size
    expected_y = layout.board_offset[1] + 1 * layout.display_cell_size
    assert frame.draw_on_calls == [(background, expected_x, expected_y)]
    assert background.draw_rect_calls[0][:2] == (expected_x, expected_y)
    assert renderer.layout.board_offset == layout.board_offset


def test_board_offset_centers_animated_piece_on_cell():
    background = FakeImage()
    canvas_size = (1000, 800)
    layout = GameUILayout.from_canvas_size(*canvas_size)
    frame = FakeImage(layout.display_cell_size, layout.display_cell_size)
    row, col = 2, 3
    cell_size = layout.display_cell_size
    board_local_center = (
        col * cell_size + cell_size / 2,
        row * cell_size + cell_size / 2,
    )
    piece = PieceSnapshot(
        piece_id=1,
        kind=PieceKind.KING,
        color=Color.WHITE,
        position=Position(row, col),
        state=PieceState.IDLE,
        visual_position=board_local_center,
    )
    renderer = make_renderer(
        background,
        lambda piece: frame,
        canvas_size=canvas_size,
    )

    renderer.render(make_snapshot([piece]))

    expected_x = layout.board_offset[0] + col * cell_size
    expected_y = layout.board_offset[1] + row * cell_size
    assert frame.draw_on_calls == [(background, int(expected_x), int(expected_y))]


def test_animated_piece_draw_position_uses_frame_dimensions():
    background = FakeImage()
    sprite_width = 80
    sprite_height = 64
    frame = FakeImage(sprite_width, sprite_height)
    canvas_size = (1000, 800)
    layout = GameUILayout.from_canvas_size(*canvas_size)
    board_local_center = (150.0, 250.0)
    piece = PieceSnapshot(
        piece_id=1,
        kind=PieceKind.ROOK,
        color=Color.WHITE,
        position=Position(2, 1),
        state=PieceState.IDLE,
        visual_position=board_local_center,
    )
    renderer = make_renderer(
        background,
        lambda piece: frame,
        canvas_size=canvas_size,
    )

    renderer.render(make_snapshot([piece]))

    expected_x = layout.board_offset[0] + board_local_center[0] - sprite_width / 2
    expected_y = layout.board_offset[1] + board_local_center[1] - sprite_height / 2
    assert frame.draw_on_calls == [(background, int(expected_x), int(expected_y))]


def test_render_places_board_background_at_board_offset():
    background = FakeImage()
    library = FakeSpriteLibrary(background)
    canvas_size = (1000, 800)
    layout = GameUILayout.from_canvas_size(*canvas_size)
    renderer = GraphicalRenderer(
        library,
        lambda: canvas_size,
        lambda piece: FakeImage(),
        FakeStateProgressOverlay(),
        FakePromotionPickerOverlay(),
        FakeMoveHistoryPanel(),
        FakeMoveHistoryPanel(),
        BoardCoordinatesRenderer(),
        PlayerPanel(),
        PlayerPanelConfig("White", "W"),
        PlayerPanelConfig("Black", "B"),
    )

    renderer.render(make_snapshot([]))

    assert library.last_board_origin == layout.board_offset
    assert library.last_canvas_size == canvas_size


def test_render_uses_bootstrap_viewport_when_canvas_size_unavailable():
    background = FakeImage()
    library = FakeSpriteLibrary(background)
    real_size = (1200, 900)
    calls = {"count": 0}

    def canvas_size_provider():
        calls["count"] += 1
        if calls["count"] == 1:
            raise ValueError("Canvas size is not available yet.")
        return real_size

    renderer = GraphicalRenderer(
        library,
        canvas_size_provider,
        lambda piece: FakeImage(),
        FakeStateProgressOverlay(),
        FakePromotionPickerOverlay(),
        FakeMoveHistoryPanel(),
        FakeMoveHistoryPanel(),
        BoardCoordinatesRenderer(),
        PlayerPanel(),
        PlayerPanelConfig("White", "W"),
        PlayerPanelConfig("Black", "B"),
    )

    renderer.render(make_snapshot([]))

    assert library.last_canvas_size == BOOTSTRAP_VIEWPORT

    renderer.render(make_snapshot([]))

    assert library.last_canvas_size == real_size


def test_render_skips_state_progress_overlay_when_progress_is_none():
    background = FakeImage()
    overlay = FakeStateProgressOverlay()
    renderer = make_renderer(background, overlay=overlay)

    renderer.render(make_snapshot([make_piece(0, 0)]))

    assert overlay.calls == []


def test_render_draws_state_progress_overlay_for_recovery_progress():
    background = FakeImage()
    overlay = FakeStateProgressOverlay()
    renderer = make_renderer(background, overlay=overlay)
    piece = PieceSnapshot(
        piece_id=1,
        kind=PieceKind.ROOK,
        color=Color.WHITE,
        position=Position(2, 3),
        state="any_state_name",
        runtime_progress={RuntimeRole.RECOVERY: 0.25},
    )

    renderer.render(make_snapshot([piece]))

    assert overlay.calls == [
        (
            background,
            renderer.layout.board_offset[0] + 3 * renderer.layout.display_cell_size,
            renderer.layout.board_offset[1] + 2 * renderer.layout.display_cell_size,
            renderer.layout.display_cell_size,
            0.25,
        ),
    ]


def test_render_skips_state_progress_overlay_for_active_ability_only():
    background = FakeImage()
    overlay = FakeStateProgressOverlay()
    renderer = make_renderer(background, overlay=overlay)
    piece = PieceSnapshot(
        piece_id=1,
        kind=PieceKind.ROOK,
        color=Color.WHITE,
        position=Position(2, 3),
        state="jump",
        runtime_progress={RuntimeRole.ACTIVE_ABILITY: 0.4},
    )

    renderer.render(make_snapshot([piece]))

    assert overlay.calls == []


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
            runtime_progress={RuntimeRole.RECOVERY: 0.0},
        ),
        PieceSnapshot(
            piece_id=2,
            kind=PieceKind.KING,
            color=Color.BLACK,
            position=Position(1, 1),
            state="beta",
            runtime_progress={RuntimeRole.RECOVERY: 0.0},
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


def test_renderer_draws_split_move_history_from_snapshot():
    background = FakeImage()
    white_history_panel = FakeMoveHistoryPanel()
    black_history_panel = FakeMoveHistoryPanel()
    renderer = make_renderer(
        background,
        white_history_panel=white_history_panel,
        black_history_panel=black_history_panel,
    )
    history = (
        MoveHistoryEntry(
            elapsed_time_ms=1000,
            piece_code="PW",
            piece_name="pawn",
            from_square="e2",
            to_square="e4",
        ),
        MoveHistoryEntry(
            elapsed_time_ms=1500,
            piece_code="PB",
            piece_name="pawn",
            from_square="e7",
            to_square="e5",
        ),
    )

    renderer.render(make_snapshot([], move_history=history))

    assert white_history_panel.draw_calls[0][:2] == (background, (history[0],))
    assert black_history_panel.draw_calls[0][:2] == (background, (history[1],))


def test_renderer_keeps_no_state_between_renders():
    renderer = make_renderer(FakeImage())

    attributes_before = set(vars(renderer))

    renderer.render(make_snapshot([make_piece(0, 0)]))
    renderer.render(make_snapshot([make_piece(1, 1)], game_over=True))

    assert set(vars(renderer)) == attributes_before
    assert set(vars(renderer)) == {
        "_sprite_library",
        "_canvas_size_provider",
        "_layout",
        "_cell_size",
        "_frame_provider",
        "_state_progress_overlay",
        "_promotion_picker_overlay",
        "_white_history_panel",
        "_black_history_panel",
        "_board_coordinates_renderer",
        "_player_panel",
        "_left_player_panel",
        "_right_player_panel",
    }
