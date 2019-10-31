import asyncio
from aioble.descriptor import Descriptor
from aioble.dotnet.utils import wrap_dotnet_task

from Windows.Devices.Bluetooth.GenericAttributeProfile import GattCommunicationStatus
from UWPBluetoothPython import UWPBluetooth


class DescriptorDotNet(Descriptor):
    """The Descriptor DotNet Class"""

    def __init__(self, characteristic, d_object, loop=None):
        super(DescriptorDotNet, self).__init__(characteristic)
        self.loop = loop if loop else asyncio.get_event_loop()
        self.characteristic = characteristic
        self.uuid = d_object.Uuid.ToString()
        self.d_object = d_object
        self._uwp_bluetooth = UWPBluetooth()

    async def read_value(self):
        """Read Characteristic Descriptor"""
        # print("Get Characteristics for {0}...".format(self.s_object.Uuid.ToString()))
        if not self.characteristic:
            raise Exception("Characteristic {0} was not found!".format(uuid))

        read_results = await wrap_dotnet_task(
            self._uwp_bluetooth.ReadDescriptorValueAsync(self.characteristic.c_object),
            loop=self.loop,
        )
        if read_results.Item2:
            status, value = read_results.Item1, bytearray(read_results.Item2)
            if status == GattCommunicationStatus.Success:
                # print("Read Characteristic {0} : {1}".format(uuid, value))
                pass
            else:
                raise Exception(
                    "Could not read descriptor value for {0}: {1}",
                    self.characteristic.Uuid.ToString(),
                    status,
                )
        else:
            return None

        return list(value)
