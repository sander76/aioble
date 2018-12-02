import asyncio

class Device(object):
    """The Device Base Class"""
    def __init__(self, identifier, loop=None):
        self.loop = loop if loop else asyncio.get_event_loop()
        self.identifier = identifier
        self.properties = None
        self.services = {}
        self._notification_callbacks = {}

    async def connect(self):
        """Connect to device"""
        raise NotImplementedError()

    async def disconnect(self):
        """Disconnect to device"""
        raise NotImplementedError()

    async def is_connected(self):
        """Is Connected to device"""
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

    async def start_notify(self):
        """Start Notification Subscription"""
        raise NotImplementedError()

    async def stop_notify(self):
        """Stop Notification Subscription"""
        raise NotImplementedError()