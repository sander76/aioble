import asyncio
from aioble import CentralManager


def callback(device, device_address, device_name):
    print(
        "device: {0} device_address: {1}  device_name: {2}".format(
            device, device_address, device_name
        )
    )


async def scan():
    try:
        cm = CentralManager()
        print("Scanning for BLE devices...")
        print("Starting")
        await cm.start_scan(callback)
        # await cm.start_scan(callback, service_uuids=["fe59"])
        await asyncio.sleep(5)
        print("Stopping")
        await cm.stop_scan()
    except Exception as e:
        print(f"Exception: {e}")


loop = asyncio.get_event_loop()
loop.run_until_complete(scan())
