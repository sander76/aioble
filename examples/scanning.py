import asyncio
from aioble import CentralManager

def callback(address, name):
    print("Address: " + address + " Name: " + name)

async def scan():
    try:
        cm = CentralManager()
        print('Scanning for BLE devices...')
        print('Starting')
        await cm.start_scan(callback)
        await asyncio.sleep(5)
        print('Stopping')
        await cm.stop_scan()
    except Exception as e:
        print(f'Exception: {e}')

loop = asyncio.get_event_loop()
loop.run_until_complete(scan())