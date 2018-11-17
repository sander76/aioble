import asyncio
from aioble import CentralManager

def callback(address, name):
    print("Address: " + address + " Name: " + name)

async def scan():
    cm = CentralManager()
    print('Scanning for BLE devices...')
    try:
        print('Starting')
        await cm.start_scan(callback)
        await asyncio.sleep(5)
    finally:
        print('Stopping')
        await cm.stop_scan()

loop = asyncio.get_event_loop()
loop.run_until_complete(scan())