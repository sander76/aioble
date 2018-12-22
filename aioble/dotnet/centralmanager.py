from aioble.centralmanager import CentralManager

from System import Array
from Windows.Devices import Enumeration
from Windows.Devices.Bluetooth import BluetoothLEDevice

class CentralManagerDotNet(CentralManager):
    """The Central Manager Dot Net Class"""
    def __init__(self, loop=None, **kwargs):
        super(CentralManagerDotNet, self).__init__(loop)
        self._device_found_callback = None
        self.devices = {}
        self._watcher = None
        self._device_found_callback = None

        self.requested_properties = Array[str](
            [
                "System.Devices.Aep.DeviceAddress",
                "System.Devices.Aep.IsConnected",
                "System.Devices.Aep.Bluetooth.Le.IsConnectable",
            ]
        )

    async def start_scan(self, callback):
        self._device_found_callback = callback
        self._watcher = Enumeration.DeviceInformation.CreateWatcher(
            BluetoothLEDevice.GetDeviceSelectorFromPairingState(False),
            self.requested_properties,
            Enumeration.DeviceInformationKind.AssociationEndpoint,
        )
        self._watcher.Added += self.DeviceWatcher_Added
        self._watcher.Updated += self.DeviceWatcher_Updated
        self._watcher.Removed += self.DeviceWatcher_Removed
        self._watcher.EnumerationCompleted += self.DeviceWatcher_EnumCompleted
        self._watcher.Stopped += self.DeviceWatcher_Stopped

        self._watcher.Start()

    def _advertisement_received(self, watcher, eventargs):
        if self._watcher == watcher:
            if eventargs.BluetoothAddress not in self.devices:
                self.devices[eventargs.BluetoothAddress] = {"Address", hex(eventargs.BluetoothAddress)}
                self._device_found_callback(eventargs, hex(eventargs.BluetoothAddress), eventargs.Advertisement.LocalName)

    async def stop_scan(self):
        """Stop Scan with timeout"""
        self._watcher.Stop()

    async def power_on(self):
        """Power on BLE Adapter"""
        raise NotImplementedError()

    async def power_off(self):
        """Power off BLE Adapter"""
        raise NotImplementedError()

    def DeviceWatcher_Added(self, sender, device_info):
        if sender == self._watcher:

            if device_info.Id not in self.devices:
                self.devices[device_info.Id] = device_info
                self._device_found_callback(device_info.Id, (device_info.Id.split('-')[-1]).upper(),
                                            device_info.Name)

    def DeviceWatcher_Updated(self, sender, device_info):
        if sender == self._watcher:
            if device_info.Id in self.devices:
                self.devices[device_info.Id].Update(device_info)

    def DeviceWatcher_Removed(self, sender, device_info):
        pass

    def DeviceWatcher_EnumCompleted(self, sender, obj):
        pass

    def DeviceWatcher_Stopped(self, sender, obj):
        pass


