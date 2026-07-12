class Controller:

    def __init__(self, board, board_mapper, game_engine):
        self.board = board
        self.board_mapper = board_mapper
        self.game_engine = game_engine
        self.selected_position = None


    def handle_click(self, x: int, y: int):

        position = self.board_mapper.pixel_to_position(
            self.board,
            x,
            y
        )

        if position is None:
            if self.selected_position is not None:
                self.selected_position = None

            return None


        if self.selected_position is None:

            piece = self.board.get_piece_by_position(position)

            if piece is None:
                return None

            self.selected_position = position
            return None


        source = self.selected_position
        self.selected_position = None

        return self.game_engine.request_move(
            source,
            position
        )