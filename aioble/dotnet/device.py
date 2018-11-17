import asyncio
from aioble.device import Device

from aioble.dotnet.utils import wrap_dotnet_task

from UWPBluetoothPython import UWPBluetooth

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

    async def disconnect(self):
        """Disconnect to device"""
        self._dotnet_task.Dispose()
        self._dotnet_task = None

    async def get_properties(self):
        """Get Device Properties"""
        raise NotImplementedError()

    async def discover_services(self):
        """Discover Device Services"""
        raise NotImplementedError()

    async def read_char(self):
        """Read Service Char"""
        raise NotImplementedError()

    async def write_char(self):
        """Write Service Char"""
        raise NotImplementedError()

    async def subscribe_to_notifications(self):
        """Connect to device"""
        raise NotImplementedError()

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