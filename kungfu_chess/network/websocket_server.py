import asyncio
import json
from typing import Callable

from kungfu_chess.events.messages.move_requested_message import MoveRequestedMessage
from kungfu_chess.model.position import Position
from kungfu_chess.network.websocket_connection import WebSocketConnection


class WebSocketServer:

    def __init__(self, game_server, host="localhost", port=8765):
        self.game_server = game_server
        self.host = host
        self.port = port
        self.clients = set()
        self.sessions = {}

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

                        print(
                            player_id,
                            "joined as",
                            session.color,
                        )

                    elif message.startswith("MOVE"):

                        print(
                            "MOVE received from",
                            player_id,
                            message,
                        )
                        
                        parts = message.split()

                        source = Position(
                            int(parts[1]),
                            int(parts[2]),
                        )

                        destination = Position(
                            int(parts[3]),
                            int(parts[4]),
                        )

                        self.sessions[player_id].receive(
                            MoveRequestedMessage(
                                source=source,
                                destination=destination,
                            )
                        )

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
