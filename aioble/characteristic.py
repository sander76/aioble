class Characteristic(object):
    """The Characteristic Base Class"""
    def __init__(self, service, c_object):
        self.service = service
        self.c_object = c_object