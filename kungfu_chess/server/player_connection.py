from dataclasses import dataclass

from kungfu_chess.server.player_color import PlayerColor
# from kungfu_chess.server.server_session import ServerSession


@dataclass
class PlayerConnection:

    player_id: str
    color: PlayerColor
    # session: ServerSession