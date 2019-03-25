class Service(object):
    """The Service Base Class"""
    def __init__(self, device, *args, **kwargs):
        self.device = device

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Service(identifier={self.identifier})"

    @property
    def identifier(self):
        """An identifier that uniquely identifies this service"""
        raise NotImplementedError()