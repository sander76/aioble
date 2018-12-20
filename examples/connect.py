import asyncio
from aioble import Device

TEST_ADDRESS_10 = 'D7:D1:17:78:FB:D0'
TEST_ADDRESS_5 = 'D4:D2:34:E3:BC:C5'
TEST_NOTIFY_CHARACTERISTIC = "ee840202-43b7-4f65-9fb9-d7b92d683e36"
TEST_WRITE_CHARACTERISTIC = "ee840203-43b7-4f65-9fb9-d7b92d683e36"

TIMEOUT_SEC = 5

config = [100, 0, 100, 0, 200, 0, 56, 255, 200, 0, 56, 255, 0]
WRITE_CHAR_TEST = bytearray(config)

def notify_callback_10(sender, data):
    values = int.from_bytes(data, byteorder='little', signed=True)
    print(f'10: {sender}: {values}')

def notify_callback_5(sender, data):
    values = int.from_bytes(data, byteorder='little', signed=True)
    print(f'5: {sender}: {values}')

def connect_callback_10():
    print("Connection to Device 10 Succeeded")

def disconnect_callback_10():
    print("Disconnection From Device 10 Succeeded")

def services_resolved_10():
    print("Services Resolved for Device 10")

def connect_callback_5():
    print("Connection to Device 5 Succeeded")

def disconnect_callback_5():
    print("Disconnection From Device 5 Succeeded")

def services_resolved_5():
    print("Services Resolved for Device 5")


async def connect_one():
    try:
        cm_10 = Device(TEST_ADDRESS_10)

        cm_10.connect_succeeded = connect_callback_10
        cm_10.disconnect_succeeded = disconnect_callback_10
        cm_10.services_resolved = services_resolved_10

        print('Connecting')

        try:
            await asyncio.wait_for(cm_10.connect(), TIMEOUT_SEC)
        except asyncio.TimeoutError:
            raise Exception("Device was not found.")
            print('Disconnecting')
            await cm_10.disconnect()

        is_c_10 = await cm_10.is_connected()
        print(f'Connected_10: {is_c_10}')

        print('Writing Char')
        await cm_10.write_char(TEST_WRITE_CHARACTERISTIC, WRITE_CHAR_TEST)

        print('Reading Char')
        print(await cm_10.read_char(TEST_WRITE_CHARACTERISTIC))

        print('Starting Notify')
        await cm_10.start_notify(TEST_NOTIFY_CHARACTERISTIC, notify_callback_10)

        await asyncio.sleep(5)

        print('Stopping Notify')
        await cm_10.stop_notify(TEST_NOTIFY_CHARACTERISTIC)

        print('Disconnecting')
        await cm_10.disconnect()

        is_c_10 = await cm_10.is_connected()
        print(f'Connected_10: {is_c_10}')

    except Exception as ex:
        print(f"Failed to Connect: {ex}")

async def connect_two():
    try:
        cm_10 = Device(TEST_ADDRESS_10)
        cm_5 = Device(TEST_ADDRESS_5)

        cm_10.connect_succeeded = connect_callback_10
        cm_10.disconnect_succeeded = disconnect_callback_10
        cm_10.services_resolved = services_resolved_10

        cm_5.connect_succeeded = connect_callback_5
        cm_5.disconnect_succeeded = disconnect_callback_5
        cm_5.services_resolved = services_resolved_5

        print('Connecting')
        tasks = [cm_10.connect(), cm_5.connect()]
        done, pending = await asyncio.wait(tasks, timeout=TIMEOUT_SEC, return_when=asyncio.ALL_COMPLETED)

        if pending:
            raise Exception("Could not connect to both devices.")

        is_c_10 = await cm_10.is_connected()
        is_c_5 = await cm_5.is_connected()
        print(f'Connected_10: {is_c_10} Connected_5: {is_c_5}')

        print('Writing Char')
        await cm_10.write_char(TEST_WRITE_CHARACTERISTIC, WRITE_CHAR_TEST)
        await cm_5.write_char(TEST_WRITE_CHARACTERISTIC, WRITE_CHAR_TEST)

        print('Reading Char')
        print(await cm_10.read_char(TEST_WRITE_CHARACTERISTIC))
        print(await cm_5.read_char(TEST_WRITE_CHARACTERISTIC))

        print('Starting Notify')
        await cm_5.start_notify(TEST_NOTIFY_CHARACTERISTIC, notify_callback_5)
        await cm_10.start_notify(TEST_NOTIFY_CHARACTERISTIC, notify_callback_10)

        await asyncio.sleep(5)

        print('Stopping Notify')
        await cm_5.stop_notify(TEST_NOTIFY_CHARACTERISTIC)
        await cm_10.stop_notify(TEST_NOTIFY_CHARACTERISTIC)

        print('Disconnecting')
        await cm_10.disconnect()
        await cm_5.disconnect()

        is_c_10 = await cm_10.is_connected()
        is_c_5 = await cm_5.is_connected()
        print(f'Connected_10: {is_c_10} Connected_5: {is_c_5}')

    except Exception as ex:
        print(f"Failed to Connect: {ex}")

loop = asyncio.get_event_loop()
loop.run_until_complete(connect_one())