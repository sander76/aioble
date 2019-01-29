import aioble
import asyncio
import argparse
import aioble

devices = []

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("device_name_prefix")
    args = parser.parse_args()

    print(f'Searching for: {args.device_name_prefix}')

    cm = aioble.CentralManager()

    found_device = asyncio.Event()

    async def did_find_device(device):
        if device.name.startswith(args.device_name_prefix):
            global devices
            devices.append(device)
            print(f'Connecting to {device}...')
            try:
                await asyncio.wait_for(device.connect(), 5)
            except:
                print("exception")
            print(f'Did Connect')
            found_device.set()

    await cm.start_scan(did_find_device)
    await asyncio.wait_for(found_device.wait(), 5)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
