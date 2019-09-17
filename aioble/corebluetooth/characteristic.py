import CoreBluetooth
import Foundation
import asyncio
from typing import List

import aioble.corebluetooth.util as util
from aioble.characteristic import Characteristic
from aioble.corebluetooth.service import CoreBluetoothService

class CoreBluetoothCharacteristic(Characteristic):
    """The CoreBluetooth implementation of a device characteristic"""
    def __init__(self, service : CoreBluetoothService, cbcharacteristic : CoreBluetooth.CBCharacteristic, queue, *args, **kwargs):
        super(CoreBluetoothCharacteristic, self).__init__(service, *args, **kwargs)
        self._cbcharacteristic = cbcharacteristic
        self._cbperipheral = cbcharacteristic.service().peripheral()
        self._queue = queue

        self._identifier = cbcharacteristic.UUID().UUIDString()

        self.read_value_future = None
        self._discover_descriptors_future = None
        self._descriptors_by_identifier = None 

    @property 
    def identifier(self):
        return self._identifier

    async def discover_descriptors(self):
        if self._descriptors_by_identifier is None:
            self._discover_descriptors_future = asyncio.Future()
            await self._discover_descriptors()
            print("here woah")
            cbdescriptors = await self._discover_descriptors_future
            print("here yeah")
            for cbdesc in cbdescriptors:
                print("uuid: ")
                print(cbdesc.UUID().UUIDString())
                self._descriptors_by_identifier = {cbdesc.UUID().UUIDString(): cbdesc}
            print("got here")
        return self._descriptors_by_identifier.values()

    @util.dispatched_to_queue(wait=False)
    def _discover_descriptors(self):
        self._cbperipheral.discoverDescriptorsForCharacteristic_(self._cbcharacteristic)
    
    def _did_discover_descriptors(self, descriptors: List[CoreBluetooth.CBDescriptor], error : Foundation.NSError):
        print("future")
        if error is not None:
            self._discover_descriptors_future.set_exception(util.NSErrorException(error))
        else:
            self._discover_descriptors_future.set_result(descriptors)

    async def read_value(self):
        if self._cbcharacteristic.properties() & CoreBluetooth.CBCharacteristicPropertyRead:
            self._read_value_future = asyncio.Future()
            await self._read_value()
            value = await self._read_value_future
            return value
        else:
            return None

    @util.dispatched_to_queue(wait=False)
    def _read_value(self):
        self._cbperipheral.readValueForCharacteristic_(self._cbcharacteristic)

    def _did_update_value(self, error : Foundation.NSError):
        future = self._read_value_future
        if future is not None:
            if error is not None:
                future.set_exception(util.NSErrorException(error))
            else:
                future.set_result(self._cbcharacteristic.value())

    async def read_value(self):
        if not self.can_read:
            self._read_value_future = asyncio.Future()
            await self._read_value()
            value = await self._read_value_future
            return value
        else:
            return None

    def can_broadcast(self):
        return self._cbcharacteristic.properties() & CoreBluetooth.CBCharacteristicPropertyBroadcast

    def can_read(self):
        return self._cbcharacteristic.properties() & CoreBluetooth.CBCharacteristicPropertyRead

    def can_write(self):
        return self._cbcharacteristic.properties() & CoreBluetooth.CBCharacteristicPropertyWrite

    def can_notify(self):
        return self._cbcharacteristic.properties() & CoreBluetooth.CBCharacteristicPropertyNotify

    def can_write_noreply(self):
        return self._cbcharacteristic.properties() & CoreBluetooth.CBCharacteristicPropertyWriteWithoutResponse

    @util.dispatched_to_queue(wait=False)
    def _read_value(self):
        self._cbperipheral.readValueForCharacteristic_(self._cbcharacteristic)

    def _did_update_value(self, error : Foundation.NSError):
        future = self._read_value_future
        if future is not None:
            if error is not None:
                future.set_exception(util.NSErrorException(error))
            else:
                future.set_result(self._cbcharacteristic.value())
