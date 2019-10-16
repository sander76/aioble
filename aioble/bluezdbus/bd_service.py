import asyncio
import re
from aioble.service import Service
from aioble.bluezdbus.bd_characteristic import CharacteristicBlueZDbus as Characteristic
import dbussy as dbus
from dbussy import \
    DBUS

_BLUEZ_DESTINATION = 'org.bluez'
_DBUS_OBJECT_MANAGER_INTERFACE = 'org.freedesktop.DBus.ObjectManager'
_GET_MANAGED_OBJECTS_METHOD = 'GetManagedObjects'

class ServiceBlueZDbus(Service):
    """The Service DotNet Class"""
    def __init__(self, device, path, uuid, loop=None):
        super(ServiceBlueZDbus, self).__init__(loop)
        self.loop = loop if loop else asyncio.get_event_loop()
        self.path = path
        self.device = device
        self.uuid = uuid
        self.characteristics = []

    async def resolve_characteristics(self):
        # Connect to system bus
        self._dbus = await dbus.Connection.bus_get_async(DBUS.BUS_SYSTEM, private=False)
        #print("Get Characteristics for {0}...".format(self.uuid))
        message = dbus.Message.new_method_call \
        (
            destination=_BLUEZ_DESTINATION,
            path="/",
            iface=_DBUS_OBJECT_MANAGER_INTERFACE,
            method=_GET_MANAGED_OBJECTS_METHOD
        )

        # Dict of {Object Path, Dict of {String, Dict of {String, Variant}}} objects)
        reply = await self._dbus.send_await_reply(message)
        values = reply.expect_return_objects("a{oa{sa{sv}}}")[0]

        characteristics_regex = re.compile(self.path + '/char[0-9abcdef]{4}$')

        self.characteristics = [Characteristic(
            service=self,
            path=objpath,
            uuid=objvalue['org.bluez.GattCharacteristic1']['UUID'][1]) for objpath, objvalue in values.items() if
            characteristics_regex.match(objpath)]

        for char in self.characteristics:
            await char.resolve_descriptors()