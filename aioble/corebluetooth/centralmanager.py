import CoreBluetooth
import Foundation
import asyncio
import functools
import libdispatch
import objc

from aioble.centralmanager import CentralManager

class CentralManagerCoreBluetooth(CentralManager):
    """Concrete implementation of the central manager protocol using CoreBluetooth API"""

    def __init__(self, loop=None, **kwargs):
        super(CentralManagerCoreBluetooth, self).__init__(loop)
        self._queue_scan_count = 0
        self._queue_isScanning = False
        self._device_found_callback = None
        self.devices = {}
        self.queue = libdispatch.dispatch_queue_create(b'CoreBluetooth Queue', libdispatch.DISPATCH_QUEUE_SERIAL)
        self._manager = CoreBluetooth.CBCentralManager.alloc().initWithDelegate_queue_options_(self, self.queue, None)

    async def start_scan(self, callback, timeout_sec = 5):
        if self._device_found_callback is not None:
            raise "Can't scan while already scanning"
        self._device_found_callback = callback
        libdispatch.dispatch_async(self.queue, self._queue_increment_scan_count)

    async def stop_scan(self, timeout_sec):
        self._device_found_callback = None
        libdispatch.dispatch_async(self.queue, self._queue_decrement_scan_count)

    def _queue_increment_scan_count(self):
        self._queue_scan_count = self._queue_scan_count + 1
        self._queue_update_scan_state_if_needed()

    def _queue_decrement_scan_count(self):
        if self._queue_scan_count > 0:
            self._queue_scan_count = self._queue_scan_count - 1
            self._queue_update_scan_state_if_needed()

    def _update_scan_state_if_needed(self):
        libdispatch.dispatch_async(self.queue, self._queue_update_scan_state_if_needed)

    def _queue_update_scan_state_if_needed(self):
        if self._manager.state() is not CoreBluetooth.CBManagerStatePoweredOn:
            return

        isScanning = self._manager.isScanning()
        if self._queue_scan_count > 0 and not isScanning:
            print("Starting Scan")
            self._manager.scanForPeripheralsWithServices_options_(None, None)
        elif self._queue_scan_count == 0 and isScanning:
            print("Stopping Scan")
            self._manager.stopScan()

    def centralManagerDidUpdateState_(self, manager):
        print("Did Update State")
        self._update_scan_state_if_needed()

    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(self, manager, peripheral, data, rssi):
        print("Found Device {}", self.loop)
        self.loop.call_soon_threadsafe(self.notify_device_found, peripheral)

    def notify_device_found(self, peripheral):
        print("Notify Device Found")
        if self._device_found_callback is not None:
            self._device_found_callback(peripheral, peripheral.name())


if __name__ == "__main__":
    manager = CentralManagerCoreBluetooth()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(10))