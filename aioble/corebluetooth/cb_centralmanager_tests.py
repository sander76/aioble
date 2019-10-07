from aioble.corebluetooth.cb_centralmanager import CoreBluetoothCentralManager
import asyncio
import pytest

pytestmark = pytest.mark.asyncio

devices = []

async def test_cb_centralmanager_initialization(event_loop: asyncio.AbstractEventLoop):
    manager = CoreBluetoothCentralManager()
    assert manager is not None

