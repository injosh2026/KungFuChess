import asyncio

from kungfu_chess.client.client import Client
from kungfu_chess.client.client_session import ClientSession
from kungfu_chess.client.network_runner import NetworkRunner
from kungfu_chess.snapshot.network_snapshot_source import NetworkSnapshotSource
from kungfu_chess.ui.network_composition_root import build_network_runner


async def start_network_game(
    image,
    connection,
):
    runner = build_network_runner(
        image,
        connection,
    )

    await runner.run()