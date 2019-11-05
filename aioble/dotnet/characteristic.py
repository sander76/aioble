import asyncio
from aioble.characteristic import Characteristic
from aioble.dotnet.descriptor import DescriptorDotNet as Descriptor
from aioble.dotnet.utils import wrap_dotnet_task

from Windows.Devices.Bluetooth.GenericAttributeProfile import (
    GattCommunicationStatus,
)
from UWPBluetoothPython import UWPBluetooth


class CharacteristicDotNet(Characteristic):
    """The Characteristic DotNet Class"""

    def __init__(self, service, c_object, loop=None):
        super(CharacteristicDotNet, self).__init__(service)
        self.loop = loop if loop else asyncio.get_event_loop()
        self.service = service
        self.uuid = c_object.Uuid.ToString()
        self.c_object = c_object
        self._uwp_bluetooth = UWPBluetooth()
        self.descriptors = []

    async def discover_descriptors(self):
        # print("Get Characteristics for {0}...".format(self.s_object.Uuid.ToString()))
        descr_results = await wrap_dotnet_task(
            self._uwp_bluetooth.GetDescriptorsAsync(self.c_object),
            loop=self.loop,
        )

        if descr_results.Status != GattCommunicationStatus.Success:
            print(
                "Could not fetch characteristics for {0}: {1}",
                self.c_object.Uuid.ToString(),
                descr_results.Status,
            )
        else:
            self.descriptors = [
                Descriptor(self, descriptor)
                for descriptor in descr_results.Descriptors
            ]
