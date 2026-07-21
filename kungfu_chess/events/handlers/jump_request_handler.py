class JumpRequestHandler:
    
    def __init__(self, game_engine):
        self._game_engine = game_engine

    def handle(self, message):
        return self._game_engine.request_jump(
            message.piece_id
        )