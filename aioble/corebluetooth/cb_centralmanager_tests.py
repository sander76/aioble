from aioble.corebluetooth.centralmanager import CentralManager
import asyncio
import pytest

pytestmark = pytest.mark.asyncio

devices = []

async def test_centralmanager(event_loop: asyncio.AbstractEventLoop):
    manager = CentralManager()
    assert True

