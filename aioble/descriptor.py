class Descriptor(object):
    """The Descriptor Base Class"""
    def __init__(self, characteristic, *args, **kwargs):
        self.characteristic = characteristic 

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Descriptor(identifier={self.identifier})"

    @property
    def identifier(self):
        """An identifier that uniquely identifies this descriptor"""
        raise NotImplementedError()