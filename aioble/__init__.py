import platform

if platform.system() == "Linux":
    from aioble.bluezdbus.centralmanager import CentralManagerBlueZDbus as CentralManager
elif platform.system() == "Darwin":
    from aioble.corebluetooth.centralmanager import CentralManagerCoreBluetooth as CentralManager
elif platform.system() == "Windows":
    from aioble.dotnet.centralmanager import CentralManagerDotNet as CentralManager