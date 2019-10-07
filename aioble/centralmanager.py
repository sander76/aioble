import abc
import asyncio

class CentralManager(abc.ABC):
    """The Central Manager Base Class"""
    def __init__(self, loop=None, *args, **kwargs):
        self.loop = loop if loop else asyncio.get_event_loop()

    @abc.abstractmethod
    async def start_scan(self, callback):
        """Start Scan with timeout"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def stop_scan(self):
        """Stop Scan with timeout"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def power_on(self):
        """Power on BLE Adapter"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def power_off(self):
        """Power off BLE Adapter"""
        raise NotImplementedError()

