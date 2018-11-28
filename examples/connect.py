import asyncio
from aioble import Device

#TEST_ADDRESS = 237293041941456
TEST_ADDRESS = 'd7:d1:17:78:fb:d0'
TEST_CHARACTERISTIC = "ee840202-43b7-4f65-9fb9-d7b92d683e36"

TEST_WRITE_CHARACTERISTIC = "ee840203-43b7-4f65-9fb9-d7b92d683e36"


mode = [100, 0, 100, 0, 200, 0, 56, 255, 200, 0, 56, 255, 0]
arrayB = bytearray(mode)

# def callback(sender, data):
#     values = int.from_bytes(data, byteorder='little', signed=True)
#     print(f"{sender}: {values}")

def callback(sender, data):
    print(f'{sender}: {data}')

async def connect():
    cm = Device(TEST_ADDRESS)
    try:
        print('Connecting')
        await cm.connect()
        x = await cm.is_connected()
        print("Connected: " + str(x))
        await cm.start_notify(TEST_CHARACTERISTIC, callback)
        #await cm.write_char(TEST_WRITE_CHARACTERISTIC, arrayB)
        #print(await cm.read_char(TEST_WRITE_CHARACTERISTIC))
        await asyncio.sleep(5)
        print('Disconnecting')
        await cm.disconnect()
        x = await cm.is_connected()
        print("Connected: " + str(x))
    except Exception as ex:
        print("Failed to Connect")
        print(f'Exception: {ex}')

loop = asyncio.get_event_loop()
loop.run_until_complete(connect())