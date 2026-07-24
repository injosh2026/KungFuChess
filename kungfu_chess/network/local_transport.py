from collections import deque
from typing import Any

from kungfu_chess.network.connection import Connection


class LocalConnection(Connection):
    """
    In-memory connection used for local multiplayer tests.

    Later replaced by WebSocket connection.
    """

    def __init__(self):
        self._incoming = deque()
        self._remote = None

    def connect_to(
        self,
        other: "LocalConnection",
    ) -> None:
        """
        Creates a two-way local connection.
        """

        self._remote = other

    def send(self, message: Any) -> None:
        """
        Sends message to remote endpoint.
        """
        if self._remote is None:
            raise RuntimeError("Connection is not connected")

        self._remote._incoming.append(message)

    def receive(self) -> Any | None:
        """
        Receives next message if available.
        """

        if not self._incoming:
            return None

        return self._incoming.popleft()
