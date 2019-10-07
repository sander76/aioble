import CoreBluetooth
import Foundation
import objc
import asyncio
from typing import List

import aioble.corebluetooth.util as util
from aioble.device import Device
from aioble.corebluetooth.cb_centralmanager import CoreBluetoothCentralManager

CoreBluetoothService = None

class CoreBluetoothDevice(Device):
    """The CoreBluetooth concrete device implementation"""
    def __init__(self, manager: CoreBluetoothCentralManager, cbperipheral : CoreBluetooth.CBPeripheral, queue, *args, **kwargs):
        super(CoreBluetoothDevice, self).__init__(manager, *args, **kwargs)
        self._cbmanager = manager._cbmanager
        self._cbperipheral = cbperipheral
        self._cbperipheral.setDelegate_(self)
        self._queue = queue

        self._identifier = self._cbperipheral.identifier().UUIDString()

        # import of services is deferred due to circular dependency
        from aioble.corebluetooth.service import CoreBluetoothService as _service
        global CoreBluetoothService
        CoreBluetoothService = _service
        self._services_by_identifier = None

        self._did_connect_event = None
        self._did_disconnect_event = None
        self._discover_services_future = None

    # Public

    @property
    def identifier(self):
        return self._identifier

    @property
    def name(self):
        return self._cbperipheral.name()

    async def connect(self):
        """Connect to device"""
        if self._did_connect_event is None:
            self._did_connect_event = asyncio.Event()
        await self._connect()
        await self._did_connect_event.wait()
        self._did_connect_event = None

    async def disconnect(self):
        """Disconnect to device"""
        if self._did_disconnect_event is None:
            self._did_disconnect_event = asyncio.Event()
        await self._disconnect()
        await self._did_disconnect_event.wait()
        self._did_disconnect_event = None

    async def is_connected(self):
        """Is Connected to device"""
        return self._cbperipheral.state() is CoreBluetooth.CBPeripheralStateConnected

    async def get_properties(self):
        """Get Device Properties"""
        raise NotImplementedError()

    async def discover_services(self) -> List[CoreBluetoothService]:
        """Discover Device Services"""
        if self._services_by_identifier is None:
            self._discover_services_future = asyncio.Future()
            await self._discover_services()
            cbservices = await self._discover_services_future
            self._services_by_identifier = {cbservice.UUID().UUIDString(): CoreBluetoothService(self, cbservice, self._queue) for cbservice in cbservices}
        return self._services_by_identifier.values()

    async def service_with_identifier(self, identifier: str) -> CoreBluetoothService:
        await self.discover_services()
        return self._services_by_identifier.get(identifier)

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
        self._cbmanager.connectPeripheral_options_(self._cbperipheral, None)

    @util.dispatched_to_loop()
    async def _did_connect(self):
        self._did_connect_event.set()

    @util.dispatched_to_queue(wait=False)
    def _disconnect(self):
        self._cbmanager.cancelPeripheralConnection_(self._cbperipheral)

    @util.dispatched_to_loop()
    async def _did_disconnect(self):
        self._did_connect_event.set()

    @util.dispatched_to_queue(wait=False)
    def _discover_services(self):
        self._cbperipheral.discoverServices_(None)

    @util.dispatched_to_loop()
    async def _did_discover_services(self, services, error):
        if error is not None:
            self._discover_services_future.set_exception(util.NSErrorException(error))
        else:
            self._discover_services_future.set_result(services)

    @util.dispatched_to_loop()
    async def _did_discover_characteristics_for_service(self, cbservice : CoreBluetooth.CBService, cbcharacteristics : List[CoreBluetooth.CBCharacteristic], error : Foundation.NSError):
        service_identifier = cbservice.UUID().UUIDString()
        service = self._services_by_identifier.get(service_identifier)
        if service is not None:
            service._did_discover_characteristics(cbcharacteristics, error)

    @util.dispatched_to_loop()
    async def _did_update_value_for_characteristic(self, cbcharacteristic : CoreBluetooth.CBCharacteristic, error : Foundation.NSError):
        cbservice = cbcharacteristic.service()
        service = self._services_by_identifier.get(cbservice.UUID().UUIDString())
        if service is None:
            return

        char = await service.characteristic_with_identifier(cbcharacteristic.UUID().UUIDString())
        if char is None:
            return

        char._did_update_value(error)

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
        self._did_discover_characteristics_for_service(service, service.characteristics(), error)

    def peripheral_didUpdateValueForCharacteristic_error_(self, peripheral, characteristic, error):
        self._did_update_value_for_characteristic(characteristic, error)

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
