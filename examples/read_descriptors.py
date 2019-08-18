import asyncio
from aioble import Device
from aioble import CentralManager

TEST_ADDRESS = 'D7:D1:17:78:FB:D0'
TEST_DESCRIPTOR_UUID = '00002902-0000-1000-8000-00805f9b34fb'

TIMEOUT_SEC = 5

d_device = None

def scan_callback(device, device_address, device_name):
    global d_device
    print("device: {0} device_address: {1}  device_name: {2}".format(device, device_address, device_name))
    if device_address == TEST_ADDRESS:
        d_device = device

def connect_callback():
    print("Connection to Device Succeeded")

def disconnect_callback(address):
    print("Disconnection From Device Succeeded, address: {0}".format(address))

def services_resolved():
    print("Services Resolved for Device ") 

async def read_descr():
    try:
        # Find Device
        cm = CentralManager()
        await cm.start_scan(scan_callback)

        while d_device is None:
            await asyncio.sleep(.1)

        await cm.stop_scan()

        # Create Device
        d = Device(d_device)

        d.connect_succeeded = connect_callback
        d.disconnect_succeeded = disconnect_callback
        d.services_resolved = services_resolved

        print('Connecting')

        try:
            await asyncio.wait_for(d.connect(), TIMEOUT_SEC)
        except asyncio.TimeoutError:
            raise Exception("Device was not found.")
            print('Disconnecting')
            await d.disconnect()

        is_d = await d.is_connected()
        print(f'Connected_10: {is_d}')

        print("\n[%s] \nResolved services" % (d.address))
        for service in d.services:
            print("\tService [%s]" % (service.uuid))
            for characteristic in service.characteristics:
                print("\t\tCharacteristic [%s]" % (characteristic.uuid))
                for descriptor in characteristic.descriptors:
                    value = await descriptor.read_value()
                    print("\t\t\tDescriptor [%s] (%s)" % (descriptor.uuid, value))

        print('Disconnecting')
        await d.disconnect()

        is_d = await d.is_connected()
        print(f'Connected_10: {is_d}')

    except Exception as ex:
        print(f"Exception, Failed to Connect: {ex}")

loop = asyncio.get_event_loop()
loop.run_until_complete(read_descr())