import platform

if platform.system() == "Linux":
    from aioble.bluezdbus.centralmanager import CentralManagerBlueZDbus as CentralManager
    from aioble.bluezdbus.device import DeviceBlueZDbus as Device
elif platform.system() == "Darwin":
    from aioble.corebluetooth.cb_centralmanager import CoreBluetoothCentralManager as CentralManager
    from aioble.corebluetooth.cb_device import CoreBluetoothDevice as Device
elif platform.system() == "Windows":
    from aioble.dotnet.centralmanager import CentralManagerDotNet as CentralManager
    from aioble.dotnet.device import DeviceDotNet as Device
else:
    from aioble.centralmanager import CentralManager
    from aioble.device import Device
    from aioble.service import Service
    from aioble.characteristic import Characteristic