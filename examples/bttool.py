import aioble
import asyncio
import argparse
import aioble
from pprint import pprint

device = None

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("device_name_prefix")
    args = parser.parse_args()

    print(f'Searching for: {args.device_name_prefix}')

    cm = aioble.CentralManager()

    found_device = asyncio.Future()

    async def did_find_device_callback(device):
        if device.name.startswith(args.device_name_prefix):
            print(f'Connecting to {device}...')
            try:
                await asyncio.wait_for(device.connect(), 5)
            except Exception as e:
                print(f'error: {e}')
            found_device.set_result(device)

    await cm.start_scan(did_find_device_callback)
    global device
    device = await asyncio.wait_for(found_device, 5)
    services = await asyncio.wait_for(device.discover_services(), 5)
    for service in services:
        print(f'service found: {service}')
        characteristics = await asyncio.wait_for(service.discover_characteristics(), 5)
        for characteristic in characteristics:
            print(f'\tcharacteristic: {characteristic} -> {await characteristic.read_value()}')
            descriptors = await characteristic.discover_descriptors()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
