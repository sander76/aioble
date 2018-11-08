import platform

if platform.system() == "Linux":
    from aioble.bluezdbus.centralmanager import CentralManagerBlueZDbus as CentralManager