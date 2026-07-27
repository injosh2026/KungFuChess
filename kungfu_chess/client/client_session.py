import inspect

from kungfu_chess.network.snapshot_deserializer import SnapshotDeserializer


class ClientSession:

    def __init__(
        self,
        player_id,
        connection,
        snapshot_source,
    ):
        self.player_id = player_id
        self.connection = connection
        self.snapshot_source = snapshot_source
        self.events = []


    async def send(self, message):
        await self.connection.send(message)


    async def receive(self):

        result = self.connection.receive()

        if inspect.isawaitable(result):
            message = await result
        else:
            message = result

        print("RAW MESSAGE:", message)

        snapshot = SnapshotDeserializer.deserialize(message)

        print("DESERIALIZED:", snapshot)
        
        if snapshot is not None:
            self.snapshot_source.update(snapshot)

        self.events.append(message)

        return message