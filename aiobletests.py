import asyncio
import pytest
pytestmark = pytest.mark.asyncio


async def wait(delay=1) -> bool:
    await asyncio.sleep(delay)
    return True

async def test_bogus(event_loop):
    assert await wait()
