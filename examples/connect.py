import asyncio
from aioble import Device

TEST_ADDRESS = 237293041941456
TEST_CHARACTERISTIC = "ee840202-43b7-4f65-9fb9-d7b92d683e36"

def callback(sender, data):
    values = int.from_bytes(data, byteorder='little', signed=True)
    print(f"{sender}: {values}")

async def connect():
    cm = Device(TEST_ADDRESS)
    try:
        print('Connecting')
        await cm.connect()
        x = await cm.is_connected()
        print("Connected: " + str(x))
        await cm.start_notify(TEST_CHARACTERISTIC, callback)
        await asyncio.sleep(5)
    finally:
        print('Disconnecting')
        await cm.disconnect()
        x = await cm.is_connected()
        print("Connected: " + str(x))

loop = asyncio.get_event_loop()
loop.run_until_complete(connect())