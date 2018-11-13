import platform

if platform.system() == "Linux":
    from aioble.bluezdbus.centralmanager import CentralManagerBlueZDbus as CentralManager
if platform.system() == "Darwin":
    from aioble.corebluetooth.centralmanager import CentralManagerCoreBluetooth as CentralManager