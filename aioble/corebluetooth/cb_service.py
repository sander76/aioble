import CoreBluetooth
import Foundation
import asyncio
from typing import List

from aioble.service import Service
from aioble.corebluetooth.cb_device import CoreBluetoothDevice
import aioble.corebluetooth.util as util

CoreBluetoothCharacteristic = None


class CoreBluetoothService(Service):
    def __init__(
        self,
        device: CoreBluetoothDevice,
        cbservice: CoreBluetooth.CBService,
        queue,
        *args,
        **kwargs
    ):
        super(CoreBluetoothService, self).__init__(device, *args, **kwargs)
        self._cbservice = cbservice
        self._queue = queue

        self._identifier = self._cbservice.UUID().UUIDString()

        # deferred import is required due to to circular dependency between characteristic and service
        from aioble.corebluetooth.characteristic import (
            CoreBluetoothCharacteristic as _characteristic,
        )

        global CoreBluetoothCharacteristic
        CoreBluetoothCharacteristic = _characteristic
        self._characteristics_by_identifier = None

        self._discover_characteristics_future = None

    @property
    def identifier(self):
        return self._identifier

    async def discover_characteristics(
        self,
    ) -> List[CoreBluetoothCharacteristic]:
        """Discover Service Characteristics"""
        if self._characteristics_by_identifier is None:
            self._discover_characteristics_future = asyncio.Future()
            await self._discover_characteristics()
            cbcharacteristics = await self._discover_characteristics_future
            self._characteristics_by_identifier = {
                cbchar.UUID().UUIDString(): CoreBluetoothCharacteristic(
                    self, cbchar, self._queue
                )
                for cbchar in cbcharacteristics
            }
        return self._characteristics_by_identifier.values()

    async def characteristic_with_identifier(
        self, identifier: str
    ) -> CoreBluetoothCharacteristic:
        await self.discover_characteristics()
        return self._characteristics_by_identifier.get(identifier)

    @util.dispatched_to_queue(wait=False)
    def _discover_characteristics(self):
        self._cbservice.peripheral().discoverCharacteristics_forService_(
            None, self._cbservice
        )

    def _did_discover_characteristics(
        self,
        characteristics: List[CoreBluetooth.CBCharacteristic],
        error: Foundation.NSError,
    ):
        if error is not None:
            self._discover_characteristics_future.set_exception(
                util.NSErrorException(error)
            )
        else:
            self._discover_characteristics_future.set_result(characteristics)
