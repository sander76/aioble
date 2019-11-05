import asyncio
from aioble.device import Device

from aioble.dotnet.utils import wrap_dotnet_task
from aioble.dotnet.service import ServiceDotNet as Service

from functools import wraps
from typing import Callable, Any

from UWPBluetoothPython import UWPBluetooth

from System import Array, Byte
from Windows.Devices.Bluetooth import BluetoothConnectionStatus
from Windows.Devices.Bluetooth.GenericAttributeProfile import (
    GattCharacteristic,
    GattCommunicationStatus,
)

from Windows.Foundation import TypedEventHandler


class DeviceDotNet(Device):
    """The Device Base Class"""

    def __init__(self, address, loop=None):
        super(DeviceDotNet, self).__init__(loop)
        self.loop = loop if loop else asyncio.get_event_loop()
        self.address_hex = hex(address)
        self.address = address
        self.properties = None
        # UWP .NET
        self._dotnet_task = None
        self._uwp_bluetooth = UWPBluetooth()
        self._devices = {}
        self.services_resolved = None
        self.is_services_resolved = False
        self.connect_succeeded = None
        self.disconnect_succeeded = None
        self.services_resolved = None

    @property
    def name(self):
        raise NotImplementedError()

    async def connect(self):
        """Connect to device"""

        # Initiate Connection
        self._dotnet_task = await wrap_dotnet_task(
            self._uwp_bluetooth.FromBluetoothAddressAsync(self.address),
            loop=self.loop,
        )

        def _ConnectionStatusChanged_Handler(sender, args):
            print("_ConnectionStatusChanged_Handler: " + args.ToString())

        # Not Working for some reason?
        self._dotnet_task.ConnectionStatusChanged += (
            _ConnectionStatusChanged_Handler
        )

        # Discover Services
        await self.discover_services()

    async def disconnect(self):
        """Disconnect to device"""
        self._dotnet_task.Dispose()
        self._dotnet_task = None

    async def is_connected(self):
        if self._dotnet_task:
            return (
                self._dotnet_task.ConnectionStatus
                == BluetoothConnectionStatus.Connected
            )

        else:
            return False

    def _services_resolved(self):
        # Notify User that Services have been Discovered
        self.is_services_resolved = True
        if self.services_resolved is not None:
            self.services_resolved()

    async def get_properties(self):
        """Get Device Properties"""
        raise NotImplementedError()

    async def discover_services(self):
        """Discover Device Services"""
        if self.services:
            return self.services
        else:
            # print("Get Services...")
            services = await wrap_dotnet_task(
                self._uwp_bluetooth.GetGattServicesAsync(self._dotnet_task),
                loop=self.loop,
            )
            if services.Status == GattCommunicationStatus.Success:
                self.services = [
                    Service(
                        device=s.Device, uuid=s.Uuid.ToString(), s_object=s
                    )
                    for s in services.Services
                ]
            else:
                raise Exception("Could not get GATT services.")

            # Discover Characteristics for Each Service
            await asyncio.gather(
                *[
                    asyncio.ensure_future(
                        service.discover_characteristics(), loop=self.loop
                    )
                    for service in self.services
                ]
            )
            self._services_resolved()

    async def read_char(self, uuid):
        """Read Service Char"""
        for s in self.services:
            for c in s.characteristics:
                if str(uuid) == c.uuid:
                    characteristic = c.c_object

        if not characteristic:
            raise Exception("Characteristic {0} was not found!".format(uuid))

        read_results = await wrap_dotnet_task(
            self._uwp_bluetooth.ReadCharacteristicValueAsync(characteristic),
            loop=self.loop,
        )
        status, value = read_results.Item1, bytearray(read_results.Item2)
        if status == GattCommunicationStatus.Success:
            # print("Read Characteristic {0} : {1}".format(uuid, value))
            pass
        else:
            raise Exception(
                "Could not read characteristic value for {0}: {1}",
                characteristic.Uuid.ToString(),
                status,
            )

        return list(value)

    async def write_char(self, uuid, data, response=False):
        """Write Service Char"""
        for s in self.services:
            for c in s.characteristics:
                if str(uuid) == c.uuid:
                    characteristic = c.c_object

        if not characteristic:
            raise Exception("Characteristic {0} was not found!".format(uuid))

        write_results = await wrap_dotnet_task(
            self._uwp_bluetooth.WriteCharacteristicValueAsync(
                characteristic, data, response
            ),
            loop=self.loop,
        )
        if write_results == GattCommunicationStatus.Success:
            # print("Write Characteristic {0} : {1}".format(uuid, data))
            pass
        else:
            raise Exception(
                "Could not write value {0} to characteristic {1}: {2}",
                data,
                characteristic.Uuid.ToString(),
                write_results,
            )

    async def start_notify(
        self, uuid, callback: Callable[[str, Any], Any], **kwargs
    ):
        """Start Notification Subscription"""
        # Find the Characteristic object
        for s in self.services:
            for c in s.characteristics:
                if str(uuid) == c.uuid:
                    characteristic = c.c_object

        if self._notification_callbacks.get(str(uuid)):
            await self.stop_notify(uuid)

        dotnet_callback = TypedEventHandler[GattCharacteristic, Array[Byte]](
            _notification_wrapper(callback)
        )
        status = await wrap_dotnet_task(
            self._uwp_bluetooth.StartNotify(characteristic, dotnet_callback),
            loop=self.loop,
        )
        if status != GattCommunicationStatus.Success:
            raise Exception(
                "Could not start notify on {0}: {1}",
                characteristic.Uuid.ToString(),
                status,
            )

    async def stop_notify(self, uuid):
        """Stop Notification Subscription"""
        # Find the Characteristic object
        for s in self.services:
            for c in s.characteristics:
                if str(uuid) == c.uuid:
                    characteristic = c.c_object
        # THIS IS NOT CURRENTLY STOPPING NOTIFICATION IMMEDIATELY
        status = await wrap_dotnet_task(
            self._uwp_bluetooth.StopNotify(characteristic), loop=self.loop
        )
        if status != GattCommunicationStatus.Success:
            raise Exception(
                "Could not start notify on {0}: {1}",
                characteristic.Uuid.ToString(),
                status,
            )

    async def read_descriptor(self, uuid):
        """Read Characteristic Descriptor"""
        for s in self.services:
            for c in s.characteristics:
                if str(uuid) == c.uuid:
                    characteristic = c.c_object

        if not characteristic:
            raise Exception("Characteristic {0} was not found!".format(uuid))

        read_results = await wrap_dotnet_task(
            self._uwp_bluetooth.ReadDescriptorValueAsync(characteristic),
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
                    characteristic.Uuid.ToString(),
                    status,
                )
        else:
            return None

        return list(value)


def _notification_wrapper(func: Callable):
    @wraps(func)
    def dotnet_notification_parser(sender: Any, data: Any):
        return func(sender.Uuid.ToString(), bytearray(data))

    return dotnet_notification_parser
