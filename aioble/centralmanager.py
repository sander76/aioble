import asyncio

class CentralManager(object):
    """The Central Manager Base Class"""

    def __init__(self, loop=None):
        self.loop = loop if loop else asyncio.get_event_loop()

    async def start_scan(self, callback):
        """Start Scan with timeout"""
        raise NotImplementedError()

    async def stop_scan(self):
        """Stop Scan with timeout"""
        raise NotImplementedError()

    async def power_on(self):
        """Power on BLE Adapter"""
        raise NotImplementedError()

    async def power_off(self):
        """Power off BLE Adapter"""
        raise NotImplementedError()

