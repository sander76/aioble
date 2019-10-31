import asyncio
import pytest
import unittest.mock
import sys

sys.modules["Foundation"] = unittest.mock.MagicMock()
sys.modules["CoreBluetooth"] = unittest.mock.MagicMock()
sys.modules["libdispatch"] = unittest.mock.MagicMock()
sys.modules["objc"] = unittest.mock.MagicMock()

from aioble.corebluetooth.cb_centralmanager import CoreBluetoothCentralManager

pytestmark = pytest.mark.asyncio


async def test_cb_centralmanager_initialization(event_loop: asyncio.AbstractEventLoop):
    manager = CoreBluetoothCentralManager()
    assert manager is not None
