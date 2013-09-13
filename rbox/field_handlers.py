import requests
import rbox
from request_handler import HttpRequest
import re
import time

resource_name_from_uri = re.compile(r".*\/(.*)\/schema\/")
id_from_uri = re.compile(r".*\/(\w+)\/")

class FieldHandler(object):

    def hydrate(self, data):
        return data

    def dehydrate(self, data, **kwargs):
        return data

class ToOneFieldHandler(FieldHandler):

    def hydrate(self, data):
        return data

    def dehydrate(self, data, **kwargs):
        #ASsumes that the data will be resource_uri
        if isinstance(data, dict):
            resource_uri = data['resource_uri']
        else:
            resource_uri = data
        new_data = get_dehydrated_object(self.schema, resource_uri)
        return new_data

class ToManyFieldHandler(ToOneFieldHandler):

    def hydrate(self, data):
        return data

    def dehydrate(self, data, **kwargs):
        new_data = []
        for obj_data in data:

            new_data.append(super(ToManyFieldHandler, self).dehydrate(obj_data))
        return new_data

class ToOneSubResourceFieldHandler(FieldHandler):

    def hydrate(self, data):
        return data

    def dehydrate(self, data, parent_obj, **kwargs):
        match = resource_name_from_uri.search(self.schema['schema'])
        if match:
            resource_name = match.groups()[0]
            subresource_list_endpoint = "%s%s/"%(parent_obj.resource_uri, resource_name)
            return getattr(parent_obj._list_object, resource_name)(list_endpoint=subresource_list_endpoint,schema_endpoint=self.schema['schema'] )
        else:
            return data

class ToManySubResourceFieldHandler(ToOneSubResourceFieldHandler):

    def hydrate(self, data):
        return data

    def dehydrate(self, data,parent_obj, **kwargs):

        return super(ToManySubResourceFieldHandler, self).dehydrate(data,parent_obj, **kwargs)


class DictFieldHandler(ToOneSubResourceFieldHandler):

    def hydrate(self, data):
        return data

    def dehydrate(self, data, **kwargs):
        return data


def get_field_handler(field_schema):

    #Another HARDCODING
    field_handler = None
    try:
        if field_schema['type'] == "related":
            field_handler = getattr(rbox.field_handlers, "%sHandler"%(field_schema['related_type']))()
        elif field_schema['type'] == "dict":
            field_handler = getattr(rbox.field_handlers, " DictFieldHandler")()
    except AttributeError:
        pass
    if field_handler:
        field_handler.schema = field_schema
        return field_handler
    return FieldHandler()



def get_dehydrated_object(schema, resource_uri, parent_obj=None):
    """This function assumes if a parent_obj is provided then it is a subresource"""

    if isinstance(resource_uri, rbox.ListResource) or \
    isinstance(resource_uri, rbox.DetailResource) or \
    hasattr(resource_uri, "_list_object"):
        #This means that the object is already dehydrated
        return resource_uri


    if resource_uri:
        match = resource_name_from_uri.search(schema['schema'])


        if match:
            resource_name = match.groups()[0]
            try:

                list_object = getattr(rbox.rbox, resource_name)
            except AttributeError:
                #THIS IS SPECIAL CASE LIKE STAGEFIELD
                #if resource_name == "stages":
                return resource_uri

                #field = ''.join([i for i in s if not i.isdigit()])

                #setattr(rbox.rbox,resource_name,type(str(resource_name), (rbox.ListResource,),\
                #    {"list_endpoint":"", "schema_endpoint" :"" })())
                #list_object = getattr(rbox.rbox, resource_name)
        else:
            return resource_uri
        id_match = id_from_uri.search(resource_uri)
        if id_match:
            id = id_match.groups()[0]
        else:
            return resource_uri

        #print "id   ",id
        return list_object.get_detail_object({"id":id}, dehydrate_object=False)
    return resource_uri
