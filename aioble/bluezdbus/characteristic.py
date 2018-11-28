from aioble.characteristic import Characteristic

class CharacteristicBlueZDbus(Characteristic):
    """The Characteristic DotNet Class"""
    def __init__(self, service, path, uuid):
        super(CharacteristicBlueZDbus, self).__init__(service)
        self.service = service
        self.uuid = uuid
        self.path = path