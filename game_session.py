from dataclasses import dataclass, field


@dataclass
class GameSession:
    board: list
    selected: tuple | None = None
    game_time: int = 0
    pending_moves: list = field(default_factory=list)
    pending_jumps: list = field(default_factory=list)
    game_over: bool = False


def create_session(board):
    return GameSession(board=board)
