import asyncio
import clr
import pathlib
from aioble.centralmanager import CentralManager

from Windows.Devices.Bluetooth.Advertisement import BluetoothLEAdvertisementWatcher

class CentralManagerDotNet(CentralManager):
    """The Central Manager Dot Net Class"""
    def __init__(self, loop=None, **kwargs):
        super(CentralManagerDotNet, self).__init__(loop)
        self._device_found_callback = None
        self.devices = {}
        self._watcher = None
        self._device_found_callback = None

    async def start_scan(self, callback):
        self._device_found_callback = callback
        self._watcher = BluetoothLEAdvertisementWatcher()
        self._watcher.Received += self._advertisement_received
        self._watcher.Start()

    def _advertisement_received(self, watcher, eventargs):
        if self._watcher == watcher:
            if eventargs.BluetoothAddress not in self.devices:
                self.devices[eventargs.BluetoothAddress] = {"Address", hex(eventargs.BluetoothAddress)}
                self._device_found_callback(hex(eventargs.BluetoothAddress), eventargs.Advertisement.LocalName)

    async def stop_scan(self):
        """Stop Scan with timeout"""
        self._watcher.Stop()

    async def power_on(self):
        """Power on BLE Adapter"""
        raise NotImplementedError()

    async def power_off(self):
        """Power off BLE Adapter"""
        raise NotImplementedError()


