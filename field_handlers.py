import requests
from request_handler import HttpRequest

class _FieldHandler(object):

    def hydrate(self, data):
        return data

    def dehydrate(self, data):
        return data


class _ToOneFieldHandler(_FieldHandler):
    pass


def get_field_handler(field_schema):

    #Another HARDCODING
    if field_schema.has_key("related_type"):
        import ipdb;ipdb.set_trace()
        field
    return _FieldHandler()
