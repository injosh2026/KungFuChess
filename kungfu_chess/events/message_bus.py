from collections import defaultdict
from collections.abc import Callable
from typing import Any, Type


class MessageBus:
    """
    Central communication channel between system components.

    Components can publish messages without knowing who will handle them.
    Handlers subscribe to specific message types and receive matching messages.

    Example:

        bus.subscribe(
            MoveRequestedMessage,
            move_handler
        )

        bus.publish(
            MoveRequestedMessage(...)
        )

    The bus itself contains no game logic.
    It only routes messages to interested handlers.
    """

    def __init__(self) -> None:
        """
        Creates an empty message bus.

        The bus starts without registered handlers.
        """
        self._handlers: dict[
            Type[Any],
            list[Callable[[Any], None]]
        ] = defaultdict(list)

    def subscribe(self, message_type: Type[Any], handler: Callable[[Any], None]) -> None:
        """
        Registers a handler for a specific message type.

        Args:
            message_type:
                The class of messages the handler accepts.

            handler:
                Function called whenever a matching message is published.

        Example:

            bus.subscribe(
                MoveRequestedMessage,
                handle_move
            )
        """
        self._handlers[message_type].append(handler)
    
    def publish(self, message: Any) -> None:
        """
        Publishes a message to all registered handlers.

        Only handlers subscribed to the exact message type
        will receive the message.

        Args:
            message:
                Message object to dispatch.
        """
        handlers = self._handlers.get(
            type(message),
            []
        )

        for handler in handlers:
            handler(message)
