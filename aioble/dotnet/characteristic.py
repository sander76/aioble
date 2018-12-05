from aioble.characteristic import Characteristic

class CharacteristicDotNet(Characteristic):
    """The Characteristic DotNet Class"""
    def __init__(self, service, c_object):
        super(CharacteristicDotNet, self).__init__(service)
        self.service = service
        self.uuid = c_object.Uuid.ToString()
        self.c_object = c_object