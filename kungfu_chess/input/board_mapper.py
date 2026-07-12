from kungfu_chess.model.position import Position


class BoardMapper:

    def __init__(self, cell_size: int):
        self.cell_size = cell_size

    def pixel_to_position(self, board, x: int, y: int) -> Position | None:

        row = y // self.cell_size
        col = x // self.cell_size

        position = Position(row, col)

        if not board.is_inside(position):
            return None

        return position