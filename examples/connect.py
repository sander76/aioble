import asyncio
from aioble import Device

TEST_ADDRESS = 237293041941456

async def connect():
    cm = Device(TEST_ADDRESS)
    try:
        print('Connecting')
        await cm.connect()
        await asyncio.sleep(5)
    finally:
        print('Disconnecting')
        await cm.disconnect()

loop = asyncio.get_event_loop()
loop.run_until_complete(connect())