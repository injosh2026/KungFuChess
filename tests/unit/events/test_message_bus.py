from dataclasses import dataclass

from kungfu_chess.events.message_bus import MessageBus


@dataclass(frozen=True)
class SampleMessage:
    """
    Simple message used only for testing MessageBus behavior.
    """
    value: str


@dataclass(frozen=True)
class OtherMessage:
    """
    Different message type used to verify type isolation.
    """
    value: str


class RecordingHandler:
    """
    Test handler that records received messages.
    """

    def __init__(self):
        self.messages = []

    def handle(self, message):
        self.messages.append(message)


def test_subscribe_receives_published_message():
    """
    A subscribed handler should receive messages
    of the matching type.
    """

    bus = MessageBus()
    handler = RecordingHandler()

    bus.subscribe(
        SampleMessage,
        handler.handle,
    )

    message = SampleMessage("hello")

    bus.publish(message)

    assert handler.messages == [message]


def test_multiple_handlers_receive_same_message():
    """
    Multiple handlers subscribed to the same message type
    should all receive the message.
    """

    bus = MessageBus()

    first = RecordingHandler()
    second = RecordingHandler()

    bus.subscribe(
        SampleMessage,
        first.handle,
    )

    bus.subscribe(
        SampleMessage,
        second.handle,
    )

    message = SampleMessage("move")

    bus.publish(message)

    assert first.messages == [message]
    assert second.messages == [message]


def test_handler_does_not_receive_different_message_type():
    """
    A handler should only receive messages for the type
    it subscribed to.
    """

    bus = MessageBus()
    handler = RecordingHandler()

    bus.subscribe(
        SampleMessage,
        handler.handle,
    )

    bus.publish(
        OtherMessage("ignored")
    )

    assert handler.messages == []