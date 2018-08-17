class GoogleMapsApiException(Exception):
    def __init__(self,value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class RequestsException(Exception):
    def __init__(self,value):
        self.value = value

    def __str__(self):
        return repr(self.value)
