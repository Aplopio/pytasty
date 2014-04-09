import requests
import pytasty
from .request_handler import HttpRequest
import re
import time
from .data_type import List

resource_name_from_uri = re.compile(r".*\/(.*)\/schema\/")
id_from_uri = re.compile(r".*\/(\w+)\/")


class FieldHandler(object):

    def hydrate(self, data):
        return data

    def dehydrate(self, data, **kwargs):
        return data


class ToOneFieldHandler(FieldHandler):

    def hydrate(self, data):
        return data.resource_uri

    def dehydrate(self, data, **kwargs):
        # ASsumes that the data will be resource_uri
        if isinstance(data, dict):
            resource_uri = data['resource_uri']
        else:
            resource_uri = data
        # if resource_uri == "/api/v1/users/25472/":
        #     import ipdb; ipdb.set_trace()
        new_data = get_dehydrated_object(self.schema, resource_uri, **kwargs)
        return new_data


class ToManyFieldHandler(ToOneFieldHandler):

    def hydrate(self, data):
        new_data = []
        for element in data:
            new_data.append(
                super(
                    ToManyFieldHandler,
                    self).hydrate(
                    data=element))
        return new_data

    def dehydrate(self, data, **kwargs):
        new_data = []
        for obj_data in data:
            new_data.append(
                super(
                    ToManyFieldHandler,
                    self).dehydrate(
                    obj_data,
                    **kwargs))
        return List(new_data)


class ToOneSubResourceFieldHandler(FieldHandler):

    def hydrate(self, data):
        return data

    def dehydrate(self, data, parent_obj, **kwargs):
        match = resource_name_from_uri.search(self.schema['schema'])
        if match:
            resource_name = match.groups()[0]
            subresource_list_endpoint = "%s%s/" % (parent_obj.resource_uri,
                                                   resource_name)
            return (
                getattr(
                    parent_obj._list_object,
                    resource_name)(list_endpoint=subresource_list_endpoint,
                                   schema_endpoint=self.schema['schema'])
            )
        else:
            return data


class ToManySubResourceFieldHandler(ToOneSubResourceFieldHandler):

    def hydrate(self, data):
        return data

    def dehydrate(self, data, parent_obj, **kwargs):
        return (
            super(
                ToManySubResourceFieldHandler,
                self).dehydrate(
                data,
                parent_obj,
                **kwargs)
        )


class DictFieldHandler(ToOneSubResourceFieldHandler):

    def hydrate(self, data):
        return data

    def dehydrate(self, data, **kwargs):
        return data


def get_field_handler(field_schema):

    # Another HARDCODING
    field_handler = None
    try:
        if field_schema['type'] == "related":
            field_handler = getattr(
                pytasty.field_handlers, "%sHandler" %
                (field_schema['related_type']))()
        elif field_schema['type'] == "dict":
            field_handler = getattr(
                pytasty.field_handlers,
                " DictFieldHandler")()
    except AttributeError:
        pass
    if field_handler:
        field_handler.schema = field_schema
        return field_handler
    return FieldHandler()


def get_dehydrated_object(schema, resource_uri, parent_obj=None, **kwargs):
    """This function assumes if a parent_obj is provided then it is a subresource"""

    if isinstance(resource_uri, pytasty.ListResource) or \
            isinstance(resource_uri, pytasty.DetailResource) or \
            hasattr(resource_uri, "_list_object"):
        # This means that the object is already dehydrated
        return resource_uri

    if resource_uri:
        match = resource_name_from_uri.search(schema['schema'])
        if match:
            resource_name = match.groups()[0]
            try:
                list_object = getattr(
                    parent_obj._list_object.api_client,
                    resource_name)
            except AttributeError:
                # THIS IS SPECIAL CASE LIKE STAGEFIELD
                return resource_uri
        else:
            return resource_uri
        id_match = id_from_uri.search(resource_uri)
        if id_match:
            id = id_match.groups()[0]
        else:
            return resource_uri
        return (
            list_object.get_detail_object(
                {"id": id,
                 "resource_uri": resource_uri},
                dehydrate_object=False)
        )
    return resource_uri
