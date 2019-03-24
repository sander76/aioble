import CoreBluetooth
import Foundation
import objc
import asyncio

import aioble.corebluetooth.util as util
from aioble.device import Device

class CoreBluetoothDevice(Device):
    """The CoreBluetooth concrete device implementation"""
    def __init__(self, manager, peripheral : CoreBluetooth.CBPeripheral, queue, loop=None, *args, **kwargs):
        super(CoreBluetoothDevice, self).__init__(loop, *args, **kwargs)
        self._manager = manager
        self._peripheral = peripheral
        self._peripheral.setDelegate_(self)
        self._queue = queue

        # Peripheral Properties
        self._identifier = self._peripheral.identifier().UUIDString()
        self._services = None

        self._did_connect_event = asyncio.Event()
        self._did_disconnect_event = asyncio.Event()
        self._did_discover_services_event = asyncio.Event()

    # Public

    @property
    def identifier(self):
        return self._identifier

    @property
    def name(self):
        return self._peripheral.name()

    async def connect(self):
        """Connect to device"""
        await self._connect()
        await self._did_connect_event.wait()

    async def disconnect(self):
        """Disconnect to device"""
        await self._disconnect()
        await self._did_disconnect_event.wait()

    async def is_connected(self):
        """Is Connected to device"""
        return self._peripheral.state() is CoreBluetooth.CBPeripheralStateConnected

    async def get_properties(self):
        """Get Device Properties"""
        raise NotImplementedError()

    async def discover_services(self):
        """Discover Device Services"""
        if self._services is None:
            self._discover_services_future = asyncio.Future()
            await self._discover_services()
            self._services = await self._discover_services_future
        return self._services

    async def read_char(self):
        """Read Service Char"""
        raise NotImplementedError()

    async def write_char(self):
        """Write Service Char"""
        raise NotImplementedError()

    async def start_notify(self):
        """Start Notification Subscription"""
        raise NotImplementedError()

    async def stop_notify(self):
        """Stop Notification Subscription"""
        raise NotImplementedError()

    # Private

    @util.dispatched_to_queue(wait=False)
    def _connect(self):
        self._manager._cbmanager.connectPeripheral_options_(self._peripheral, None)

    @util.dispatched_to_loop()
    async def _did_connect(self):
        self._did_connect_event.set()

    @util.dispatched_to_queue(wait=False)
    def _disconnect(self):
        self._manager._cbmanager.cancelPeripheralConnection_(self._peripheral)

    @util.dispatched_to_loop()
    async def _did_disconnect(self):
        self._did_connect_event.set()

    @util.dispatched_to_queue(wait=False)
    def _discover_services(self):
        self._peripheral.discoverServices_(None)

    @util.dispatched_to_loop()
    async def _did_discover_services(self, services, error):
        if services is None:
            self._discover_services_future.set_exception(util.NSErrorException(error))
        else:
            self._discover_services_future.set_result(services)

    # CBPeripheralDelegate

    def peripheralDidUpdateName_(self, peripheral):
        pass

    def peripheral_didModifyServices_(self, peripheral, services):
        pass

    def peripheralDidUpdateRSSI_error_(self, peripheral, rssi, error):
        pass

    def peripheral_didReadRSSI_error_(self, peripheral, rssi, error):
        pass

    def peripheral_didDiscoverServices_(self, peripheral, error):
        self._did_discover_services(peripheral.services(), error)

    def peripheral_didDiscoverIncludedServices_error_(self, peripheral, service, error):
        pass

    def peripheral_didDiscoverCharacteristicsForService_error_(self, peripheral, service, error):
        pass

    def peripheral_didUpdateValueForCharacteristic_error_(self, peripheral, characteristic, error):
        pass

    def peripheral_didWriteValueForCharacteristic_error_(self, peripheral, characteristic, error):
        pass

    def peripheral_didUpdateNotificationStateForCharacteristic_error_(self, peripheral, characteristic, error):
        pass

    def peripheral_didDiscoverDescriptorsForCharacteristic_error_(self, peripheral, characteristic, error):
        pass

    def peripheral_didUpdateValueForDescriptor_error_(self, peripheral, descriptor, error):
        pass

    def peripheral_didWriteValueForDescriptor_error_(self, peripheral, descriptor, error):
        pass

    def peripheralIsReadyToSendWriteWithoutResponse_(self, peripheral):
        pass

    def peripheral_didOpenL2CAPChannel_error_(self, peripheral, channel, error):
        pass