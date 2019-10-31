from aioble.centralmanager import CentralManager
import abc
import asyncio
import pytest

pytestmark = pytest.mark.asyncio


async def test_centralmanager_is_baseclass(event_loop: asyncio.AbstractEventLoop):
    assert issubclass(CentralManager, abc.ABC)
