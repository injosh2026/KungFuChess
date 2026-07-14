from kungfu_chess.model.position import Position


class BoardMapper:
    """
    Converts external pixel coordinates into board positions.

    BoardMapper is responsible only for translating input
    coordinates. It does not handle selection, movement rules,
    or game logic.
    """

    def __init__(self, cell_size: int):
        """
        Creates a mapper for a board with a given cell size.

        Args:
            cell_size:
                Size of one board cell in pixels.
        """
        self.cell_size = cell_size

    def pixel_to_position(self, board, x: int, y: int) -> Position | None:
        """
        Converts screen coordinates into a board position.

        Args:
            board:
                Board used to validate boundaries.

            x:
                Horizontal pixel coordinate.

            y:
                Vertical pixel coordinate.

        Returns:
            The matching Position if the coordinates are inside
            the board, otherwise None.
        """
        row = y // self.cell_size
        col = x // self.cell_size

        position = Position(row, col)

        if not board.is_inside(position):
            return None

        return position
