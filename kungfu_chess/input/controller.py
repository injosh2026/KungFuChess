class Controller:

    def __init__(self, board, board_mapper, game_engine):
        self.board = board
        self.board_mapper = board_mapper
        self.game_engine = game_engine
        self._selected_position = None


    @property
    def selected_position(self):
        return self._selected_position


    def handle_click(self, x: int, y: int):

        position = self.board_mapper.pixel_to_position(
            self.board,
            x,
            y
        )

        if position is None:
            if self._selected_position is not None:
                self._selected_position = None

            return None


        if self._selected_position is None:

            piece = self.board.get_piece_by_position(position)

            if piece is None:
                return None

            self._selected_position = position
            return None


        source = self._selected_position
        self._selected_position = None

        return self.game_engine.request_move(
            source,
            position
        )