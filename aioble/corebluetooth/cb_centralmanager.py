import CoreBluetooth
import Foundation
import asyncio
import functools
import libdispatch
import objc

import aioble.corebluetooth.util as util
from aioble.centralmanager import CentralManager

CoreBluetoothDevice = None

class CoreBluetoothCentralManager(CentralManager):
    """Concrete implementation of the central manager protocol using CoreBluetooth API"""

    def __init__(self, loop=None, *args, **kwargs):
        super(CoreBluetoothCentralManager, self).__init__(loop, *args, **kwargs)
        self._lock = asyncio.Lock()
        self._queue_scan_count = 0
        self._queue_isScanning = False
        self._device_found_callback = None
        self._queue = libdispatch.dispatch_queue_create(b'CoreBluetooth Queue', libdispatch.DISPATCH_QUEUE_SERIAL)
        self._cbmanager = CoreBluetooth.CBCentralManager.alloc().initWithDelegate_queue_options_(self, self._queue, None)

        # We need to defer the import of CoreBluetoothDevice due to circular dependency
        from aioble.corebluetooth.cb_device import CoreBluetoothDevice as _device
        global CoreBluetoothDevice
        CoreBluetoothDevice = _device
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

    async def power_on(self):
        pass

    async def power_off(self):
        pass

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
        self._queue_update_scan_state_if_needed()

    def _queue_update_scan_state_if_needed(self, cbmanager = None):
        if cbmanager is None:
            cbmanager = self._cbmanager
        if cbmanager.state() is not CoreBluetooth.CBManagerStatePoweredOn:
            return
        isScanning = cbmanager.isScanning()
        if self._queue_scan_count > 0 and not isScanning:
            cbmanager.scanForPeripheralsWithServices_options_(None, None)
        elif self._queue_scan_count == 0 and isScanning:
            cbmanager.stopScan()
        self._queue_isScanning = cbmanager.isScanning()

    @util.dispatched_to_loop()
    async def _notify_device_found(self, peripheral : CoreBluetooth.CBPeripheral):
        async with self._lock:
            if self._device_found_callback is not None:
                device = self.devices.get(peripheral.identifier().UUIDString())
                if device is None:
                    device = CoreBluetoothDevice(manager=self, cbperipheral=peripheral, queue=self._queue)
                    self.devices[device.identifier] = device
                    if asyncio.iscoroutinefunction(self._device_found_callback):
                        await self._device_found_callback(device)
                    else:
                        self._device_found_callback(device)

    @util.dispatched_to_loop()
    async def _peripheral_did_connect(self, peripheral : CoreBluetooth.CBPeripheral):
        device = self.devices.get(peripheral.identifier().UUIDString())
        if device:
            device._did_connect()

    @util.dispatched_to_loop()
    async def _peripheral_did_disconnect(self, peripheral : CoreBluetooth.CBPeripheral):
        device = self.devices.get(peripheral.identifier().UUIDString())
        if device:
            device._did_disconnect()

    # CBCentralManagerDelegate

    def centralManagerDidUpdateState_(self, manager):
        self._queue_update_scan_state_if_needed(cbmanager = manager)

    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(self, manager, peripheral, data, rssi):
        self._notify_device_found(peripheral)

    def centralManager_didConnectPeripheral_(self, manager, peripheral):
        self._peripheral_did_connect(peripheral)

    def centralManager_didDisconnectPeripheral_(self, manager, peripheral):
        self._peripheral_did_disconnect(peripheral)
