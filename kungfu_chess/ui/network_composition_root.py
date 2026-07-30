"""
Builds all UI dependencies and starts GameApp.

This module is the composition root:
it connects existing components but contains no game logic.
"""

from collections.abc import Callable
from types import SimpleNamespace

from kungfu_chess.client.client import Client
from kungfu_chess.client.client_session import ClientSession
from kungfu_chess.client.connection_command_sender import ConnectionCommandSender
from kungfu_chess.client.network_runner import NetworkRunner
from kungfu_chess.config.demo_config import (
    ASSETS_ROOT,
    BOARD_FILENAME,
    PIECE_SET,
    STARTING_BOARD,
)
from kungfu_chess.engine.game_factory import GameFactory
from kungfu_chess.events.handlers.jump_request_handler import JumpRequestHandler
from kungfu_chess.events.handlers.move_request_handler import MoveRequestHandler
from kungfu_chess.events.handlers.promotion_request_handler import (
    PromotionRequestHandler,
)
from kungfu_chess.events.message_bus import MessageBus
from kungfu_chess.events.messages.jump_requested_message import JumpRequestedMessage
from kungfu_chess.events.messages.move_requested_message import MoveRequestedMessage
from kungfu_chess.events.messages.promotion_requested_message import (
    PromotionRequestedMessage,
)
from kungfu_chess.input.board_mapper import BoardMapper
from kungfu_chess.input.click_router import ClickRouter
from kungfu_chess.input.controller import Controller
from kungfu_chess.input.mouse_input import MouseInput
from kungfu_chess.io.board_parser import BoardParser
from kungfu_chess.rules.pawn_end_outcome import PendingPawnPromotion
from kungfu_chess.snapshot.network_snapshot_source import NetworkSnapshotSource
from kungfu_chess.ui.animation_clock import AnimationClock
from kungfu_chess.ui.animation_provider import AnimationProvider
from kungfu_chess.ui.board_coordinates_renderer import BoardCoordinatesRenderer
from kungfu_chess.ui.game_app import GameApp
from kungfu_chess.ui.board_click_mapper import window_coords_to_model_coords
from kungfu_chess.ui.game_ui_layout import layout_for_canvas_size_provider
from kungfu_chess.ui.graphical_renderer import GraphicalRenderer
from kungfu_chess.ui.move_history_panel import MoveHistoryPanel
from kungfu_chess.ui.player_panel import PlayerPanel
from kungfu_chess.ui.player_panel_data import PlayerPanelConfig
from kungfu_chess.ui.promotion_picker_overlay import PromotionPickerOverlay
from kungfu_chess.ui.sprite_library import SpriteLibrary
from kungfu_chess.ui.state_progress_overlay import StateProgressOverlay

MODEL_CELL_SIZE = GameFactory.CELL_SIZE
SPRITE_LIBRARY_BOOTSTRAP_CELL_SIZE = 1


def to_model_coords(
    x: int,
    y: int,
    canvas_size_provider: Callable[[], tuple[int, int]],
) -> tuple[int, int]:
    """
    Translates a window pixel into the model's pixel space so the unchanged
    board mapper resolves the same cell the user clicked on screen.
    """
    layout = layout_for_canvas_size_provider(canvas_size_provider)
    return window_coords_to_model_coords(
        x,
        y,
        layout,
        MODEL_CELL_SIZE,
    )


def build_network_runner(
    image,
    connection,
) -> NetworkRunner:
    board_parser = BoardParser()
    board = board_parser.parse(STARTING_BOARD)
    board_mapper = BoardMapper(MODEL_CELL_SIZE)
    message_bus = MessageBus()
    command_sender = ConnectionCommandSender(connection)

    message_bus.subscribe(
        MoveRequestedMessage,
        MoveRequestHandler(command_sender).handle,
    )
    message_bus.subscribe(
        JumpRequestedMessage,
        JumpRequestHandler(command_sender).handle,
    )
    message_bus.subscribe(
        PromotionRequestedMessage,
        PromotionRequestHandler(command_sender).handle,
    )

    game_queries = SimpleNamespace(
        is_piece_in_cooldown=lambda piece_id: False,
        get_legal_moves=lambda position: set(),
    )

    controller = Controller(
        board,
        board_mapper,
        game_queries,
        message_bus,
    )

    canvas_size = image.canvas_size

    library = SpriteLibrary(
        ASSETS_ROOT / PIECE_SET,
        ASSETS_ROOT / BOARD_FILENAME,
        SPRITE_LIBRARY_BOOTSTRAP_CELL_SIZE,
    )
    clock = AnimationClock()
    provider = AnimationProvider(library, clock)
    promotion_picker = PromotionPickerOverlay()
    white_history_panel = MoveHistoryPanel("White")
    black_history_panel = MoveHistoryPanel("Black")
    board_coordinates_renderer = BoardCoordinatesRenderer()
    player_panel = PlayerPanel()
    renderer = GraphicalRenderer(
        library,
        canvas_size,
        provider.frame_for,
        StateProgressOverlay(),
        promotion_picker,
        white_history_panel,
        black_history_panel,
        board_coordinates_renderer,
        player_panel,
        PlayerPanelConfig("White", "W"),
        PlayerPanelConfig("Black", "B"),
    )

    snapshot_source = NetworkSnapshotSource(
        connection,
        controller=controller,
    )

    client_session = ClientSession(
        "player",
        connection,
        snapshot_source,
    )

    def sync_controller_board_from_snapshot() -> None:
        snapshot = snapshot_source.get_snapshot()
        if snapshot is not None:
            controller.board = board_parser.from_snapshot(snapshot)

    def handle_board_click(x: int, y: int):
        sync_controller_board_from_snapshot()
        return controller.handle_click(
            *to_model_coords(x, y, canvas_size),
        )

    def get_pending_promotion():
        snapshot = snapshot_source.get_snapshot()
        if snapshot is None or snapshot.pending_promotion is None:
            return None

        pending = snapshot.pending_promotion
        return PendingPawnPromotion(
            piece_id=pending.piece_id,
            allowed_kinds=pending.allowed_kinds,
        )

    click_router = ClickRouter(
        controller,
        promotion_picker,
        get_pending_promotion,
        handle_board_click,
        canvas_size,
    )

    mouse_input = MouseInput(click_router)

    wait_target = SimpleNamespace(wait=lambda milliseconds: None)

    game_app = GameApp(
        wait_target,
        controller,
        snapshot_source,
        renderer,
        image,
        clock,
        mouse_input,
    )

    client = Client(
        client_session,
    )

    return NetworkRunner(
        client,
        game_app,
    )
