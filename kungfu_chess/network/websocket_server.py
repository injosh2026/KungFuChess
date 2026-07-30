from kungfu_chess.events.messages.jump_requested_message import JumpRequestedMessage
from kungfu_chess.events.messages.move_requested_message import MoveRequestedMessage
from kungfu_chess.events.messages.promotion_requested_message import (
    PromotionRequestedMessage,
)
from kungfu_chess.network.websocket_connection import WebSocketConnection


class WebSocketServer:

    def __init__(self, game_server, host="localhost", port=8765):
        self.game_server = game_server
        self.host = host
        self.port = port
        self.clients = set()
        self.sessions = {}

    def receive_input_command(self, player_id: str, message_text: str) -> bool:
        """
        Translates a wire-format input command into a domain message
        and forwards it to the player's server session.
        """
        domain_message = self._parse_input_command(message_text)

        if domain_message is None:
            return False

        self.sessions[player_id].receive(domain_message)
        return True

    @staticmethod
    def _parse_input_command(message_text: str):
        if message_text.startswith("MOVE"):
            return MoveRequestedMessage.from_wire_format(message_text)

        if message_text.startswith("JUMP"):
            return JumpRequestedMessage.from_wire_format(message_text)

        if message_text.startswith("PROMOTION"):
            return PromotionRequestedMessage.from_wire_format(message_text)

        return None

    async def start(self):

        import websockets

        async def handler(websocket):
            player_id = None
            self.clients.add(websocket)

            try:
                async for message in websocket:
                    if message.startswith("JOIN"):

                        player_id = message.split()[1]

                        connection = WebSocketConnection(websocket)

                        session = self.game_server.join_match(
                            "match1",
                            player_id,
                            connection,
                        )

                        self.sessions[player_id] = session

                        session.send_initial_snapshot()

                        session.send_snapshot(None)

                        print(
                            player_id,
                            "joined as",
                            session.color,
                        )

                    elif (
                        message.startswith("MOVE")
                        or message.startswith("JUMP")
                        or message.startswith("PROMOTION")
                    ):

                        print(
                            "Input command received from",
                            player_id,
                            message,
                        )

                        self.receive_input_command(player_id, message)
                    else:
                        await self.broadcast(message)

            finally:
                self.clients.remove(websocket)

        self.server = await websockets.serve(
            handler,
            self.host,
            self.port,
        )

    async def broadcast(self, message):

        for client in self.clients:
            await client.send(message)

    async def stop(self):

        self.server.close()

        await self.server.wait_closed()
