class Characteristic(object):
    """The Characteristic Base Class"""
    def __init__(self, service, *args, **kwargs):
        self.service = service

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Characteristic(identifier={self.identifier})"

    @property
    def identifier(self):
        """An identifier that uniquely identifies this characteristic"""
        raise NotImplementedError()