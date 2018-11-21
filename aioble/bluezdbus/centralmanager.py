import asyncio
import sys
import json
import re
import dbussy as dbus
from dbussy import \
    DBUS

from aioble.centralmanager import CentralManager

_BLUEZ_DESTINATION = 'org.bluez'

_BLUEZ_OBJECT_PATH = '/org/bluez/hci0'

_ADAPTER_INTERFACE = 'org.bluez.Adapter1'
_PROPERTIES_INTERFACE = 'org.freedesktop.DBus.Properties'

_INTROSPECT_METHOD = 'Introspect'
_START_DISCOVERY_METHOD = 'StartDiscovery'
_STOP_DISCOVERY_METHOD = 'StopDiscovery'
_SET_DISCOVERY_FILTER_METHOD = 'SetDiscoveryFilter'

_DISCOVERY_FILTER_ARGS = ['{"Transport": ["s", "le"]}']


class CentralManagerBlueZDbus(CentralManager):
    """The Central Manager Bluez Dbus Class"""

    def __init__(self, loop=None, **kwargs):
        super(CentralManagerBlueZDbus, self).__init__(loop)
        self.device = kwargs.get("device", "hci0")
        self._device_found_callback = None
        self.devices = {}
        self._dbus = None

    async def start_scan(self, callback):
        # Set callback for new devices
        self._device_found_callback = callback

        # Set device path regex
        self._device_path_regex = re.compile('^/org/bluez/' + 'hci0' + '/dev((_[A-Z0-9]{2}){6})$')

        # Connect to system bus
        self._dbus = await dbus.Connection.bus_get_async(DBUS.BUS_SYSTEM, private = False)

         # Perform Introspection
        message = dbus.Message.new_method_call(destination = _BLUEZ_DESTINATION, path = _BLUEZ_OBJECT_PATH, iface = DBUS.INTERFACE_INTROSPECTABLE, method = _INTROSPECT_METHOD)
        reply = await self._dbus.send_await_reply(message)
        introspection = dbus.Introspection.parse(reply.expect_return_objects("s")[0])

        # Assign Interfaces
        self._interfaces = introspection.interfaces_by_name
        self._adapter_interface = self._interfaces[_ADAPTER_INTERFACE]
        self._properties_interface = self._interfaces[_PROPERTIES_INTERFACE]

        # Assign Adapter Interface Methods
        self._adapter_interface_methods = self._adapter_interface.methods_by_name
        _set_discovery_filters_method = self._adapter_interface_methods[_SET_DISCOVERY_FILTER_METHOD]

        # Get method signature
        message = dbus.Message.new_method_call(destination = _BLUEZ_DESTINATION, path = _BLUEZ_OBJECT_PATH, iface = _ADAPTER_INTERFACE, method = _SET_DISCOVERY_FILTER_METHOD)
        sig = dbus.parse_signature(_set_discovery_filters_method.in_signature)

        #sig = dbus.parse_signature("e{sv}")

        # Deserialize json string
        argobjs = list(sig[i].validate(json.loads(_DISCOVERY_FILTER_ARGS[i])) for i in range(len(sig)))

        # Call SetDiscovery Filter method with arguments
        message.append_objects(sig, *argobjs)
        reply = await self._dbus.send_await_reply(message)

        # Start Discovery
        self._dbus.add_filter(self.signal_parser, None)
        self._dbus.bus_add_match({"type" : "signal", "interface" : "org.freedesktop.DBus.ObjectManager", "member" : "InterfacesAdded", "interface" : "org.freedesktop.DBus.Properties", "member" : "PropertiesChanged", "arg0": "org.bluez.Device1"}) 
        
        # Get method signature
        message = dbus.Message.new_method_call(destination = _BLUEZ_DESTINATION, path = _BLUEZ_OBJECT_PATH, iface = _ADAPTER_INTERFACE, method = _START_DISCOVERY_METHOD)

        await self._dbus.send_await_reply(message)

        # Add Devices that are already known
        await self._update_devices()

    async def stop_scan(self):
        """Stop Scan"""
        # Remove Signal Filter
        # THIS IS SEG FAULTING?
        # self._dbus.remove_filter(self.signal_parser, None)
        self._dbus.bus_remove_match({"type" : "signal", "interface" : "org.freedesktop.DBus.ObjectManager", "member" : "InterfacesAdded", "interface" : "org.freedesktop.DBus.Properties", "member" : "PropertiesChanged", "arg0": "org.bluez.Device1"})
        # Get method signature
        message = dbus.Message.new_method_call(destination = _BLUEZ_DESTINATION, path = _BLUEZ_OBJECT_PATH, iface = _ADAPTER_INTERFACE, method = _STOP_DISCOVERY_METHOD)

        await self._dbus.send_await_reply(message)

    async def power_on(self):
        """Power on BLE Adapter"""
        raise NotImplementedError()

    async def power_off(self):
        """Power off BLE Adapter"""
        raise NotImplementedError()

    async def _update_devices(self):
        """Interface Added Signal"""
        message = dbus.Message.new_method_call(destination = _BLUEZ_DESTINATION, path = '/', iface = 'org.freedesktop.DBus.ObjectManager', method = 'GetManagedObjects')
        reply = await self._dbus.send_await_reply(message)
        for interfaces in reply.all_objects:
            for path in interfaces:
                if 'org.bluez.Device1' in interfaces[path]:
                    #Adding New Device
                    self._add_new_device(path, interfaces[path]["org.bluez.Device1"])

    def _add_new_device(self, path, properties):
        """Add New Device Found"""
        if path not in self.devices:
            self.devices[path] = properties
            # Add Address field from dbus path if no Address field exist
            if "Address" not in self.devices[path]:
                match = self._device_path_regex.match(path)
                address = match.group(1)[1:].replace('_', ':').lower()
                addressDict = {'Address': (type(address), address.upper())}
                properties = {**properties, **addressDict}
                #Update with Address field
                self.devices[path] = properties
            # Call Callback with new devices found
            if "Address" in self.devices[path] and "Alias" in self.devices[path]:
                self._device_found_callback(self.devices[path]["Address"][1], self.devices[path]["Alias"][1])
            elif "Address" in self.devices[path]:
                self._device_found_callback(self.devices[path]["Address"][1], "<unknown>")

    def signal_parser(self, connection, message, data):
        """Interface Added Signal"""
        if message.type == DBUS.MESSAGE_TYPE_SIGNAL :
            if message.member == "InterfacesAdded":
                if message.interface == "org.bluez.Device1":
                    if message.path not in self.devices:
                        # Add New Device
                        self._add_new_device(message.path, message.interface["org.bluez.Device1"])
                        
            elif message.member == 'PropertiesChanged':
                for e in message.objects:
                    if(e != "org.bluez.Device1"):
                        return DBUS.HANDLER_RESULT_HANDLED
                    else:
                        properties = list(message.objects)[1]
                        if message.path not in self.devices:
                            # Add New Device with new property
                            self._add_new_device(message.path, properties)
                        else:
                            # Update Existing Device with changed properties
                            self._add_new_device(message.path, {**self.devices[message.path], **properties})
            
        return DBUS.HANDLER_RESULT_HANDLED
