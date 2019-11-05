import asyncio
import re
from aioble.characteristic import Characteristic
from aioble.bluezdbus.bd_descriptor import DescriptorBlueZDbus as Descriptor
import dbussy as dbus
from dbussy import DBUS

_BLUEZ_DESTINATION = "org.bluez"
_DBUS_OBJECT_MANAGER_INTERFACE = "org.freedesktop.DBus.ObjectManager"
_GET_MANAGED_OBJECTS_METHOD = "GetManagedObjects"


class CharacteristicBlueZDbus(Characteristic):
    """The Characteristic DotNet Class"""

    def __init__(self, service, path, uuid, loop=None):
        super(CharacteristicBlueZDbus, self).__init__(service)
        self.loop = loop if loop else asyncio.get_event_loop()
        self.service = service
        self.uuid = uuid
        self.path = path

    async def resolve_descriptors(self):
        # Connect to system bus
        self._dbus = await dbus.Connection.bus_get_async(
            DBUS.BUS_SYSTEM, private=False
        )

        message = dbus.Message.new_method_call(
            destination=_BLUEZ_DESTINATION,
            path="/",
            iface=_DBUS_OBJECT_MANAGER_INTERFACE,
            method=_GET_MANAGED_OBJECTS_METHOD,
        )

        # Dict of {Object Path, Dict of {String, Dict of {String, Variant}}} objects)
        reply = await self._dbus.send_await_reply(message)
        values = reply.expect_return_objects("a{oa{sa{sv}}}")[0]

        descriptor_regex = re.compile(self.path + "/desc[0-9abcdef]{4}$")
        self.descriptors = [
            Descriptor(
                characteristic=self,
                path=objpath,
                uuid=objvalue["org.bluez.GattDescriptor1"]["UUID"][1],
            )
            for objpath, objvalue in values.items()
            if descriptor_regex.match(objpath)
        ]

        # print(self.uuid)
        # for d in self.descriptors:
        #     try:
        #         print("d.path:")
        #         print(d.path)
        #     except:
        #         print("no descriptor")
