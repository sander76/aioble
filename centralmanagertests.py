from aioble import CentralManager
import asyncio
import pytest

pytestmark = pytest.mark.asyncio

devices = []

def callback(device, device_name):
    print("Callback: Found device {}", device)
    devices.append(device)
    assert device is None
    assert device_name is None

async def test_centralmanager(event_loop: asyncio.AbstractEventLoop):
    manager = CentralManager()
    await manager.start_scan(callback)
    await asyncio.sleep(5)
    assert manager is not None
    assert devices.__len__() == 0

