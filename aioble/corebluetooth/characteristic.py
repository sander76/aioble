import CoreBluetooth

import aioble.corebluetooth.util as util
from aioble.characteristic import Characteristic
from aioble.corebluetooth.service import CoreBluetoothService

class CoreBluetoothCharacteristic(Characteristic):
    """The CoreBluetooth implementation of a device characteristic"""
    def __init__(self, service : CoreBluetoothService, cbcharacteristic : CoreBluetooth.CBCharacteristic, *args, **kwargs):
        super(CoreBluetoothCharacteristic, self).__init__(service, *args, **kwargs)
        self._cbcharacteristic = cbcharacteristic
        self._cbperipheral = cbcharacteristic.service().peripheral()

        self._identifier = cbcharacteristic.UUID().UUIDString()

    @property
    def identifier(self):
        return self._identifier
