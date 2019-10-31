from aioble.descriptor import Descriptor
import dbussy as dbus
from dbussy import DBUS

_BLUEZ_DESTINATION = "org.bluez"
_GATT_DESCRIPTOR_INTERFACE = "org.bluez.GattDescriptor1"
_READ_VALUE_METHOD = "ReadValue"


class DescriptorBlueZDbus(Descriptor):
    """The Characteristic DotNet Class"""

    def __init__(self, characteristic, path, uuid):
        super(DescriptorBlueZDbus, self).__init__(characteristic)
        self.characteristic = characteristic
        self.uuid = uuid
        self.path = path

    async def read_value(self):
        """Read Characteristic Descriptor"""
        # Connect to system bus
        self._dbus = await dbus.Connection.bus_get_async(DBUS.BUS_SYSTEM, private=False)

        try:
            # Assemble Read Value Method Message
            message = dbus.Message.new_method_call(
                destination=dbus.valid_bus_name(_BLUEZ_DESTINATION),
                path=dbus.valid_path(self.path),
                iface=_GATT_DESCRIPTOR_INTERFACE,
                method=_READ_VALUE_METHOD,
            )
            message.append_objects("a{sv}", {})
        except Exception as ex:
            print("Exception, Invalid Descriptor Path")

        try:
            reply = await self._dbus.send_await_reply(message)
            values = reply.expect_return_objects("ay")[0]
            return values
        except:
            return []
