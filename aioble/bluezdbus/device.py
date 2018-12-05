import asyncio
from aioble.device import Device
import sys
import re
import dbussy as dbus
from dbussy import \
    DBUS

from aioble.bluezdbus.service import ServiceBlueZDbus as Service

_BLUEZ_DESTINATION = 'org.bluez'

_BLUEZ_OBJECT_PATH = '/org/bluez/hci0'

_DEVICE_INTERFACE = 'org.bluez.Device1'
_GATT_CHARACTERISTIC_INTERFACE = 'org.bluez.GattCharacteristic1'
_DBUS_OBJECT_MANAGER_INTERFACE = 'org.freedesktop.DBus.ObjectManager'

_CONNECT_METHOD = 'Connect'
_DISCONNECT_METHOD = 'Disconnect'
_START_NOTIFY_METHOD = 'StartNotify'
_STOP_NOTIFY_METHOD = 'StopNotify'
_WRITE_VALUE_METHOD = 'WriteValue'
_READ_VALUE_METHOD = 'ReadValue'
_GET_MANAGED_OBJECTS_METHOD = 'GetManagedObjects'

class DeviceBlueZDbus(Device):
    """The Device Base Class"""

    def __init__(self, address, loop=None):
        super(DeviceBlueZDbus, self).__init__(loop)
        self.loop = loop if loop else asyncio.get_event_loop()
        self.address = address
        self.properties = None
        self._notification_callbacks = {}
        self._dbus = None

    async def connect(self):
        """Connect to device"""

        self._device_path = '/org/bluez/%s/dev_%s' % ('hci0', self.address.replace(':', '_').upper())

        # Connect to system bus
        self._dbus = await dbus.Connection.bus_get_async(DBUS.BUS_SYSTEM, private = False, loop = self.loop)

        # Assemble Connect Method Message
        message = dbus.Message.new_method_call \
        (
            destination = dbus.valid_bus_name(_BLUEZ_DESTINATION),
            path = self._device_path,
            iface = _DEVICE_INTERFACE,
            method = _CONNECT_METHOD
        )

        # Connect
        await self._dbus.send_await_reply(message)

        if await self.is_connected():
            print("Connection successful.")
        else:
            raise Exception("Connection unsuccessful.")

        if not self.services and await self.is_services_resolved():
            await self.discover_services()

    def signal_parser(self, connection, message, data):
        """Interface Added Signal"""
        if message.type == DBUS.MESSAGE_TYPE_SIGNAL:
            if message.member == "PropertiesChanged":
                if message.interface == "org.freedesktop.DBus.Properties":
                    #print(self.address)
                    if message.path in self._notification_callbacks:
                        if 'Value' in list(message.objects)[1]:
                            # Call Callback with Data
                            self._notification_callbacks[message.path](message.path, list(message.objects)[1]['Value'][1])
                        elif 'Notifying' in list(message.objects)[1]:
                            pass
                            # Notifying Property Value
                            #print(list(message.objects)[1]['Notifying'][1])
            return DBUS.HANDLER_RESULT_HANDLED

    async def disconnect(self):
        """Disconnect to device"""

        # Assemble Disonnect Method Message
        message = dbus.Message.new_method_call \
        (
            destination = dbus.valid_bus_name(_BLUEZ_DESTINATION),
            path = dbus.valid_path(self._device_path),
            iface = _DEVICE_INTERFACE,
            method = _DISCONNECT_METHOD)

        await self._dbus.send_await_reply(message)

    async def is_connected(self):
        """Is Connected to device"""

        # Assemble IsConnected Method Message
        message = dbus.Message.new_method_call \
        (
            destination = dbus.valid_bus_name(_BLUEZ_DESTINATION),
            path = dbus.valid_path(self._device_path),
            iface = DBUS.INTERFACE_PROPERTIES,
            method = "Get"
        )
        message.append_objects("s", dbus.valid_interface(_DEVICE_INTERFACE))
        message.append_objects("s", "Connected")
        reply = await self._dbus.send_await_reply(message)

        # Return Boolean IsConnected
        return reply.expect_return_objects("v")[0][1]

    async def read_char(self, uuid):
        """Read Service Char"""

        char_path = ""

        for s in self.services:
            for c in s.characteristics:
                if uuid == c.uuid:
                    char_path = c.path

        # Assemble Read Value Method Message
        message = dbus.Message.new_method_call \
        (
            destination = dbus.valid_bus_name(_BLUEZ_DESTINATION),
            path = dbus.valid_path(char_path),
            iface = _GATT_CHARACTERISTIC_INTERFACE,
            method = _READ_VALUE_METHOD
        )
        message.append_objects("a{sv}", {})

        reply = await self._dbus.send_await_reply(message)
        values = reply.expect_return_objects("ay")[0]
        return values

    async def write_char(self, uuid, data):
        """Write Service Char"""

        char_path = ""

        for s in self.services:
            for c in s.characteristics:
                if uuid == c.uuid:
                    char_path = c.path

        bytes = [DBUS.subtype_byte(b) for b in data]

        # Assemble Write Value Method Message
        message = dbus.Message.new_method_call \
        (
            destination = dbus.valid_bus_name(_BLUEZ_DESTINATION),
            path = dbus.valid_path(char_path),
            iface = _GATT_CHARACTERISTIC_INTERFACE,
            method = _WRITE_VALUE_METHOD
        )
        message.append_objects("ay", bytes)
        message.append_objects("a{sv}", {})

        try:
            reply = await self._dbus.send_await_reply(message)
            values = reply.expect_return_objects("")
        except dbus.DBusError:
            return ""

    async def start_notify(self, uuid, callback):
        """Start Notification Subscription"""

        char_path = ""

        for s in self.services:
            for c in s.characteristics:
                if uuid == c.uuid:
                    char_path = c.path

        # Add callback to active notify subscriptions
        self._notification_callbacks[char_path] = callback

        rule = {"type": "signal", "interface": "org.freedesktop.DBus.Properties", "member": "PropertiesChanged",
            "arg0": "org.bluez.GattCharacteristic1", "path": char_path}

        await self._dbus.bus_add_match_action_async(rule, self.signal_parser, None)

        # Assemble Start Notify Method Message
        message = dbus.Message.new_method_call \
        (
            destination = dbus.valid_bus_name(_BLUEZ_DESTINATION),
            path = dbus.valid_path(char_path),
            iface = _GATT_CHARACTERISTIC_INTERFACE,
            method = _START_NOTIFY_METHOD
        )

        await self._dbus.send_await_reply(message)

    async def stop_notify(self, uuid):
        """Stop Notification Subscription"""

        char_path = ""

        for s in self.services:
            for c in s.characteristics:
                if uuid == c.uuid:
                    char_path = c.path

        # Remove callback to active notify subscriptions
        del self._notification_callbacks[char_path]

        rule = {"type": "signal", "interface": "org.freedesktop.DBus.Properties", "member": "PropertiesChanged",
            "arg0": "org.bluez.GattCharacteristic1", "path": char_path}

        await self._dbus.bus_remove_match_action_async(rule, self.signal_parser, None)

        # Assemble Stop Notify Method Message
        message = dbus.Message.new_method_call \
        (
            destination = dbus.valid_bus_name(_BLUEZ_DESTINATION),
            path = dbus.valid_path(char_path),
            iface = _GATT_CHARACTERISTIC_INTERFACE,
            method = _STOP_NOTIFY_METHOD
        )

        await self._dbus.send_await_reply(message)

    async def is_services_resolved(self):
        """Is Services Resolved"""

        # Assemble Get Method Message
        message = dbus.Message.new_method_call \
        (
            destination = dbus.valid_bus_name(_BLUEZ_DESTINATION),
            path = dbus.valid_path(self._device_path),
            iface = DBUS.INTERFACE_PROPERTIES,
            method = "Get"
        )
        message.append_objects("s", dbus.valid_interface(_DEVICE_INTERFACE))
        message.append_objects("s", 'ServicesResolved')
        reply = await self._dbus.send_await_reply(message)

        return reply.expect_return_objects("v")[0]

    async def discover_services(self):
        """Discover Device Services"""

        if self.services:
            return self.services
        else:
            print("Get Services...")
            message = dbus.Message.new_method_call \
            (
                destination= dbus.valid_bus_name(_BLUEZ_DESTINATION),
                path= dbus.valid_path("/"),
                iface= _DBUS_OBJECT_MANAGER_INTERFACE,
                method= _GET_MANAGED_OBJECTS_METHOD
            )
            # Dict of {Object Path, Dict of {String, Dict of {String, Variant}}} objects)
            reply = await self._dbus.send_await_reply(message)
            values = reply.expect_return_objects("a{oa{sa{sv}}}")[0]

            services_regex = re.compile(self._device_path + '/service[0-9abcdef]{4}$')

            self.services = [Service(
                device=self,
                path=objpath,
                uuid=objvalue['org.bluez.GattService1']['UUID'][1]) for objpath, objvalue in values.items() if
                services_regex.match(objpath)]

            for service in self.services:
                await service.resolve_characteristics()

    async def _get_properties(self):
        """Get Properties"""

        # Assemble GetAll Properties Method Message
        message = dbus.Message.new_method_call \
        (
            destination = dbus.valid_bus_name(_BLUEZ_DESTINATION),
            path = dbus.valid_path(self._device_path),
            iface = DBUS.INTERFACE_PROPERTIES,
            method = "GetAll"
        )
        message.append_objects("s", dbus.valid_interface(_DEVICE_INTERFACE))
        reply = await self._dbus.send_await_reply(message)
        values = reply.expect_return_objects("a{sv}")[0]
        print(values)
        for propname in sorted(values.keys()) :
            proptype, propvalue = values[propname]
            sys.stdout.write("%s(%s) = %s\n" % (propname, proptype, repr(propvalue)))