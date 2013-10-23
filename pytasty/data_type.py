class List(list):
    def append(self, value, **kwargs):
        raise AttributeError("Cannot use append!")
