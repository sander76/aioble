import asyncio
import pytest
import unittest.mock
import sys

sys.modules['Foundation'] = unittest.mock.MagicMock()
sys.modules['CoreBluetooth'] = unittest.mock.MagicMock()
sys.modules['libdispatch'] = unittest.mock.MagicMock()
sys.modules['objc'] = unittest.mock.MagicMock()

from aioble.bluezdbus.centralmanager import CentralManagerBlueZDbus

pytestmark = pytest.mark.asyncio

async def test_centralmanager_initialization(event_loop: asyncio.AbstractEventLoop):
    manager = CentralManagerBlueZDbus()
    assert manager is not None

