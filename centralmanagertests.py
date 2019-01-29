from aioble import CentralManager
import asyncio
import pytest

pytestmark = pytest.mark.asyncio

devices = []

def callback(device):
    print("Callback: Found device: ", device.identifier, device.name)
    devices.append(device)

async def test_centralmanager(event_loop: asyncio.AbstractEventLoop):
    manager = CentralManager()
    await manager.start_scan(callback)
    await asyncio.sleep(5)
    assert manager is not None
    assert devices.__len__() == 0

