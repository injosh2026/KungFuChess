from abc import ABC, abstractmethod
from typing import Any


class Connection(ABC):
    """
    Abstract communication channel.

    Implementations can be local memory transport,
    WebSocket, TCP, etc.
    """

    @abstractmethod
    def send(self, message: Any) -> None:
        """
        Sends a message through the connection.
        """
        pass


    @abstractmethod
    def receive(self) -> Any | None:
        """
        Receives the next available message.
        """
        pass