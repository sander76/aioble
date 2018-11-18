import asyncio
from aioble.device import Device

from aioble.dotnet.utils import wrap_dotnet_task

from functools import wraps
from typing import Callable, Any

from UWPBluetoothPython import UWPBluetooth

from System import Array, Byte
from Windows.Devices.Bluetooth import BluetoothConnectionStatus
from Windows.Devices.Bluetooth.GenericAttributeProfile import (
    GattCharacteristic, GattCommunicationStatus
)

from Windows.Foundation import TypedEventHandler

class DeviceDotNet(Device):
    """The Device Base Class"""
    def __init__(self, address, loop=None):
        super(DeviceDotNet, self).__init__(loop)
        self.loop = loop if loop else asyncio.get_event_loop()
        self.address = address
        self.properties = None
        #UWP .NET 
        self._dotnet_task = None
        self._uwp_bluetooth = UWPBluetooth()
        
    async def connect(self):
        """Connect to device"""
        self._dotnet_task = await wrap_dotnet_task(
            self._uwp_bluetooth.FromBluetoothAddressAsync(self.address),
            loop=self.loop,
        )

        def _ConnectionStatusChanged_Handler(sender, args):
            print("_ConnectionStatusChanged_Handler: " + args.ToString())

        self._dotnet_task.ConnectionStatusChanged += _ConnectionStatusChanged_Handler

        serv = await self.discover_services()

    async def disconnect(self):
        """Disconnect to device"""
        self._dotnet_task.Dispose()
        self._dotnet_task = None

    async def is_connected(self):
        if self._dotnet_task:
            return self._dotnet_task.ConnectionStatus == BluetoothConnectionStatus.Connected

        else:
            return False

    async def get_properties(self):
        """Get Device Properties"""
        raise NotImplementedError()

    async def discover_services(self):
        """Discover Device Services"""
        if self.services:
            return self.services
        else:
            print("Get Services...")
            services = await wrap_dotnet_task(
                self._uwp_bluetooth.GetGattServicesAsync(self._dotnet_task), loop=self.loop
            )
            if services.Status == GattCommunicationStatus.Success:
                self.services = {s.Uuid.ToString(): s for s in services.Services}
            else:
                raise Exception("Could not get GATT services.")

            await asyncio.gather(
                *[
                    asyncio.ensure_future(self._discover_char(service), loop=self.loop)
                    for service_uuid, service in self.services.items()
                ]
            )
            self._services_resolved = True
            return self.services

    async def _discover_char(self, service):
        print("Get Characteristics for {0}...".format(service.Uuid.ToString()))
        char_results = await wrap_dotnet_task(
            self._uwp_bluetooth.GetCharacteristicsAsync(service), loop=self.loop
        )

        if char_results.Status != GattCommunicationStatus.Success:
            print(
                "Could not fetch characteristics for {0}: {1}",
                service.Uuid.ToString(),
                char_results.Status,
            )
        else:
            for characteristic in char_results.Characteristics:
                self.characteristics[characteristic.Uuid.ToString()] = characteristic

    async def read_char(self):
        """Read Service Char"""
        raise NotImplementedError()

    async def write_char(self):
        """Write Service Char"""
        raise NotImplementedError()

    async def start_notify(self, uuid, callback: Callable[[str, Any], Any], **kwargs):
        """Start Notification Subscription"""
        characteristic = self.characteristics.get(str(uuid))

        if self._notification_callbacks.get(str(uuid)):
            await self.stop_notify(uuid)

        dotnet_callback = TypedEventHandler[GattCharacteristic, Array[Byte]](
            _notification_wrapper(callback)
        )
        status = await wrap_dotnet_task(
            self._uwp_bluetooth.StartNotify(characteristic, dotnet_callback), loop=self.loop
        )
        if status != GattCommunicationStatus.Success:
            raise Exception(
                "Could not start notify on {0}: {1}",
                characteristic.Uuid.ToString(),
                status,
            )

    async def stop_notify(self, uuid):
        """Stop Notification Subscription"""
        characteristic = self.characteristics.get(str(uuid))
        status = await wrap_dotnet_task(
            self._bridge.StopNotify(characteristic), loop=self.loop
        )
        if status != GattCommunicationStatus.Success:
            raise Exception(
                "Could not start notify on {0}: {1}",
                characteristic.Uuid.ToString(),
                status,
            )

def _notification_wrapper(func: Callable):
    @wraps(func)
    def dotnet_notification_parser(sender: Any, data: Any):
        return func(sender.Uuid.ToString(), bytearray(data))
    return dotnet_notification_parser

class Service(object):
    """The Service Base Class"""
    def __init__(self, device, uuid):
        self.device = device
        self.characteristics = []
    
class Characteristic(object):
    """The Characteristic Base Class"""
    def __init__(self, service, uuid):
        self.service = service
        self.uuid = uuid