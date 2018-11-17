import asyncio

class Device(object):
    """The Device Base Class"""
    def __init__(self, address, loop=None):
        self.loop = loop if loop else asyncio.get_event_loop()
        self.address = address
        #self.manager = manager
        self.properties = None

    async def connect(self):
        """Connect to device"""
        raise NotImplementedError()

    async def disconnect(self):
        """Disconnect to device"""
        raise NotImplementedError()

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