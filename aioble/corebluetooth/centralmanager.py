import CoreBluetooth
import Foundation
import asyncio
import functools
import libdispatch
import objc
import weakref

from aioble.centralmanager import CentralManager

def dispatched_to_queue(method=None, wait=True):
    def func(method):
        @functools.wraps(method)
        async def wrapper(self, *args, **kwargs):
            if wait:
                loop = asyncio.get_event_loop()
                future = loop.create_future()
                def queue_block():
                    result = method(self, *args, **kwargs)
                    def loop_block():
                        future.set_result(result)
                    loop.call_soon_threadsafe(loop_block)
                libdispatch.dispatch_async(self._queue, queue_block)
                return await future
            else:
                def queue_block():
                    method(self, *args, **kwargs)
                libdispatch.dispatch_async(self._queue, queue_block)
                return None
        return wrapper
    return func

def dispatched_to_loop(method=None):
    def func(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            asyncio.run_coroutine_threadsafe(functools.partial(method, self, *args, **kwargs)(), self.loop)
        return wrapper
    return func


class CentralManagerCoreBluetooth(CentralManager):
    """Concrete implementation of the central manager protocol using CoreBluetooth API"""

    def __init__(self, loop=None, *args, **kwargs):
        super(CentralManagerCoreBluetooth, self).__init__(loop, *args, **kwargs)
        self._lock = asyncio.Lock()
        self._queue = libdispatch.dispatch_queue_create(b'CoreBluetooth Queue', libdispatch.DISPATCH_QUEUE_SERIAL)
        self._delegate = _CentralManagerDelegate(self)
        self._manager = CoreBluetooth.CBCentralManager.alloc().initWithDelegate_queue_options_(self._delegate, self._queue, None)
        self._queue_scan_count = 0
        self._queue_isScanning = False
        self._device_found_callback = None
        self.devices = {}

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

    @dispatched_to_queue()
    def _increment_scan_count(self):
        self._queue_scan_count = self._queue_scan_count + 1
        self._queue_update_scan_state_if_needed()

    @dispatched_to_queue()
    def _decrement_scan_count(self):
        if self._queue_scan_count > 0:
            self._queue_scan_count = self._queue_scan_count - 1
            self._queue_update_scan_state_if_needed()

    @dispatched_to_queue()
    def _update_scan_state_if_needed(self):
        self._queue_update_scan_state_if_needed

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
        self._queue_isScanning = self._manager.isScanning()

    @dispatched_to_loop()
    async def _notify_device_found(self, peripheral):
        async with self._lock:
            print("Notify Device Found")
            if self._device_found_callback is not None:
                self._device_found_callback(peripheral, peripheral.name())


class _CentralManagerDelegate():
    def __init__(self, manager : CentralManagerCoreBluetooth, *args, **kwargs):
        self.managerref = weakref.ref(manager)

    def centralManagerDidUpdateState_(self, manager):
        self.managerref()._queue_update_scan_state_if_needed()

    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(self, manager, peripheral, data, rssi):
        self.managerref()._notify_device_found(peripheral)