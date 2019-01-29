import CoreBluetooth
import Foundation
import asyncio
import functools
import libdispatch
import objc
import weakref

import aioble.corebluetooth.util as util
from aioble.centralmanager import CentralManager

class CoreBluetoothCentralManager(CentralManager):
    """Concrete implementation of the central manager protocol using CoreBluetooth API"""

    def __init__(self, loop=None, *args, **kwargs):
        super(CoreBluetoothCentralManager, self).__init__(loop, *args, **kwargs)
        self._lock = asyncio.Lock()
        self._queue = libdispatch.dispatch_queue_create(b'CoreBluetooth Queue', libdispatch.DISPATCH_QUEUE_SERIAL)
        self._cbmanager = CoreBluetooth.CBCentralManager.alloc().initWithDelegate_queue_options_(self, self._queue, None)
        self._queue_scan_count = 0
        self._queue_isScanning = False
        self._device_found_callback = None
        self.devices = {}

    # Public

    async def start_scan(self, callback):
        async with self._lock:
            if self._device_found_callback is not None:
                raise "Can't scan while already scanning"
            self._device_found_callback = callback
            await self._increment_scan_count()

    async def stop_scan(self):
        async with self._lock:
            self._device_found_callback = None
            await self._decrement_scan_count()

    # Private

    @util.dispatched_to_queue()
    def _increment_scan_count(self):
        self._queue_scan_count = self._queue_scan_count + 1
        self._queue_update_scan_state_if_needed()

    @util.dispatched_to_queue()
    def _decrement_scan_count(self):
        if self._queue_scan_count > 0:
            self._queue_scan_count = self._queue_scan_count - 1
            self._queue_update_scan_state_if_needed()

    @util.dispatched_to_queue()
    def _update_scan_state_if_needed(self):
        self._queue_update_scan_state_if_needed

    def _queue_update_scan_state_if_needed(self):
        if self._cbmanager.state() is not CoreBluetooth.CBManagerStatePoweredOn:
            return
        isScanning = self._cbmanager.isScanning()
        if self._queue_scan_count > 0 and not isScanning:
            self._cbmanager.scanForPeripheralsWithServices_options_(None, None)
        elif self._queue_scan_count == 0 and isScanning:
            self._cbmanager.stopScan()
        self._queue_isScanning = self._cbmanager.isScanning()

    @util.dispatched_to_loop()
    async def _notify_device_found(self, peripheral):
        async with self._lock:
            if self._device_found_callback is not None:
                self._device_found_callback(peripheral, peripheral.name())


    # CBCentralManagerDelegate

    def centralManagerDidUpdateState_(self, manager):
        self._queue_update_scan_state_if_needed()

    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(self, manager, peripheral, data, rssi):
        self._notify_device_found(peripheral)
