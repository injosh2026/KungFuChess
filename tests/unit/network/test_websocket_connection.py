import asyncio
import threading

from kungfu_chess.network.websocket_connection import WebSocketConnection


class FakeWebSocket:

    def __init__(self):
        self.sent_messages = []
        self._send_completed = threading.Event()

    async def send(self, message):
        self.sent_messages.append(message)
        self._send_completed.set()

    async def recv(self):
        await asyncio.Event().wait()


def test_websocket_connection_send_from_external_thread_schedules_websocket_send():
    fake_websocket = FakeWebSocket()

    async def run():
        connection = WebSocketConnection(fake_websocket)

        ui_thread = threading.Thread(
            target=connection.send,
            args=("MOVE 0 0 0 1",),
        )
        ui_thread.start()
        ui_thread.join(timeout=1)

        deadline = asyncio.get_running_loop().time() + 1
        while (
            not fake_websocket._send_completed.is_set()
            and asyncio.get_running_loop().time() < deadline
        ):
            await asyncio.sleep(0.01)

        assert fake_websocket.sent_messages == ["MOVE 0 0 0 1"]

    asyncio.run(run())
