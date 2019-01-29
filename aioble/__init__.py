import platform

if platform.system() == "Linux":
    from aioble.bluezdbus.centralmanager import CentralManagerBlueZDbus as CentralManager
    from aioble.bluezdbus.device import DeviceBlueZDbus as Device
elif platform.system() == "Darwin":
    from aioble.corebluetooth.centralmanager import CoreBluetoothCentralManager as CentralManager
elif platform.system() == "Windows":
    from aioble.dotnet.centralmanager import CentralManagerDotNet as CentralManager
    from aioble.dotnet.device import DeviceDotNet as Device