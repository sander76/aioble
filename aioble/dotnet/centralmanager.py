from aioble.centralmanager import CentralManager

from Windows.Devices.Bluetooth.Advertisement import BluetoothLEAdvertisementWatcher

class CentralManagerDotNet(CentralManager):
    """The Central Manager Dot Net Class"""
    def __init__(self, loop=None, **kwargs):
        super(CentralManagerDotNet, self).__init__(loop)
        self._device_found_callback = None
        self.devices = {}
        self._watcher = None
        self._device_found_callback = None
        self.service_uuids = None

    async def start_scan(self, callback, service_uuids=[]):
        self._device_found_callback = callback
        self.service_uuids = service_uuids
        self._watcher = BluetoothLEAdvertisementWatcher()
        self._watcher.Received += self._advertisement_received
        self._watcher.Start()

    def _advertisement_received(self, watcher, eventargs):
        if self._watcher == watcher:
            s_uuid = [str(i) for i in list(eventargs.Advertisement.ServiceUuids)]
            if self.service_uuids:
                if any(x in self.service_uuids for x in s_uuid):
                    if eventargs.BluetoothAddress not in self.devices:
                        self.devices[eventargs.BluetoothAddress] = {"Address", hex(eventargs.BluetoothAddress)}
                        s = (str(hex(eventargs.BluetoothAddress)))[2:].upper()
                        self._device_found_callback(eventargs.BluetoothAddress,
                                                    ':'.join(a + b for a, b in zip(s[::2], s[1::2])),
                                                    eventargs.Advertisement.LocalName)
            else:
                if eventargs.BluetoothAddress not in self.devices:
                    self.devices[eventargs.BluetoothAddress] = {"Address", hex(eventargs.BluetoothAddress)}
                    s = (str(hex(eventargs.BluetoothAddress)))[2:].upper()
                    self._device_found_callback(eventargs.BluetoothAddress,
                                                ':'.join(a+b for a,b in zip(s[::2], s[1::2])),
                                                eventargs.Advertisement.LocalName)

    async def stop_scan(self):
        """Stop Scan with timeout"""
        self._watcher.Stop()
#
    async def power_on(self):
        """Power on BLE Adapter"""
        raise NotImplementedError()

    async def power_off(self):
        """Power off BLE Adapter"""
        raise NotImplementedError()