import asyncio
from aioble.service import Service
from aioble.dotnet.dn_characteristic import CharacteristicDotNet as Characteristic
from aioble.dotnet.dn_utils import wrap_dotnet_task

from Windows.Devices.Bluetooth.GenericAttributeProfile import (
    GattCommunicationStatus,
)
from UWPBluetoothPython import UWPBluetooth


class ServiceDotNet(Service):
    """The Service DotNet Class"""

    def __init__(self, device, uuid, s_object, loop=None):
        super(ServiceDotNet, self).__init__(loop)
        self.loop = loop if loop else asyncio.get_event_loop()
        self.device = device
        self.s_object = s_object
        self.uuid = uuid
        self.characteristics = []
        self._dotnet_task = None
        self._uwp_bluetooth = UWPBluetooth()

    async def discover_characteristics(self):
        # print("Get Characteristics for {0}...".format(self.s_object.Uuid.ToString()))
        char_results = await wrap_dotnet_task(
            self._uwp_bluetooth.GetCharacteristicsAsync(self.s_object),
            loop=self.loop,
        )

        if char_results.Status != GattCommunicationStatus.Success:
            print(
                "Could not fetch characteristics for {0}: {1}",
                self.s_object.Uuid.ToString(),
                char_results.Status,
            )
        else:
            self.characteristics = [
                Characteristic(self, characteristic)
                for characteristic in char_results.Characteristics
            ]

        for characteristic in self.characteristics:
            await characteristic.discover_descriptors()
