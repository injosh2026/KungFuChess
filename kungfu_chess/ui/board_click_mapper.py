from kungfu_chess.model.position import Position
from kungfu_chess.ui.game_ui_layout import GameUILayout


def window_coords_to_position(
    x: int,
    y: int,
    layout: GameUILayout,
) -> Position | None:
    board_rect = layout.board_rect
    cell_size = layout.display_cell_size

    local_x = x - board_rect.x
    local_y = y - board_rect.y

    if (
        local_x < 0
        or local_y < 0
        or local_x >= board_rect.width
        or local_y >= board_rect.height
    ):
        return None

    col = local_x // cell_size
    row = local_y // cell_size
    return Position(row, col)


def window_coords_to_model_coords(
    x: int,
    y: int,
    layout: GameUILayout,
    model_cell_size: int,
) -> tuple[int, int]:
    board_rect = layout.board_rect
    cell_size = layout.display_cell_size

    local_x = x - board_rect.x
    local_y = y - board_rect.y

    model_x = local_x * model_cell_size // cell_size
    model_y = local_y * model_cell_size // cell_size
    return model_x, model_y
