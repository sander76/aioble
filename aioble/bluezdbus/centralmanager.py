import asyncio

from aioble.centralmanager import CentralManager

class CentralManagerBlueZDbus(CentralManager):
    """The Central Manager Base Class"""

    def __init__(self, loop=None, **kwargs):
        super(CentralManagerBlueZDbus, self).__init__(loop)
        self.device = kwargs.get("device", "hci0")

    async def start_scan(self, timeout_sec = 5):
        """Start Scan with timeout"""
        await asyncio.sleep(timeout_sec)

    async def stop_scan(self, timeout_sec = 5):
        """Stop Scan with timeout"""
        await asyncio.sleep(timeout_sec)

    async def power_on(self):
        """Power on BLE Adapter"""
        raise NotImplementedError()

    async def power_off(self):
        """Power off BLE Adapter"""
        raise NotImplementedError()

