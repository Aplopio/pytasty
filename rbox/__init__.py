from request_handler import HttpRequest
import time
import requests
#import rbox
from StringIO import StringIO
from utils import  dehydrate, get_schema
from field_handlers import get_field_handler
from data_type import List

class ListResource(object):

    def __init__(self, *args, **kwargs):
        self._generate_detail_class()

    def _generate_schema(self):
        self.schema = get_schema(self.schema_endpoint)
        self._update_listsubresource()

    def _update_listsubresource(self):
        if not hasattr(self, "schema"):
            self._generate_schema()
        for field_name, field_schema in self.schema['fields'].iteritems():
            if field_schema['type'] == "related" and \
               field_schema['related_type'] in ["ToOneSubResourceField","ToManySubResourceField"] :
                setattr(self, field_name, type(str(field_name), (ListSubResource,), {}) )

    def _generate_detail_class(self):
        if not hasattr(self, "schema"):
            self._generate_schema()

        class_name = self.__class__.__name__
        if class_name.endswith("s"):
            class_name = class_name[:-1]
        class_name = class_name.capitalize()

        setattr(rbox, class_name,type(class_name, (self.default_detail_class,), {"_list_object":self}) )
        self._detail_class = getattr(rbox, class_name)
        return self._detail_class

    def get_detail_object(self, json_obj, dehydrate_object=True):
        if not hasattr(self, "_detail_class"):
            self._generate_detail_class()

        detail_object = self._detail_class()
        detail_object.__dict__['json'] = json_obj
        for field_name, field_value in json_obj.iteritems():
            detail_object.__dict__[field_name] = field_value

        if dehydrate_object == True:
            return dehydrate(detail_object)
        else:
            return detail_object

    def all(self, **kwargs):

        response_objects = _request_handler.request("GET", self.list_endpoint, [__USERNAME__,__API_KEY__] )
        next_url = response_objects['meta']['next']
        objects = response_objects['objects']

        while True:
            for obj in objects:
                yield self.get_detail_object(obj)
            if next_url:
                response_objects = _request_handler.request("GET", __SITE__ + next_url, [__USERNAME__,__API_KEY__] )
                next_url = response_objects['meta']['next']
                objects = response_objects['objects']
            else:
                break

    def get(self, offset=0, limit=20, **kwargs):
        response_objects = _request_handler.request("GET", self.list_endpoint, [__USERNAME__,__API_KEY__] )

        #ONE HARDCODING
        for list_meta_name,list_meta_value in response_objects.pop("meta").iteritems():
            setattr(self, list_meta_name, list_meta_value)

        return [self.get_detail_object(obj) for obj in response_objects['objects']]


    def retrieve(self, id):
        response_object = _request_handler.request("GET", "%s%s/"%(self.list_endpoint, id), [__USERNAME__,__API_KEY__] )
        return self.get_detail_object(response_object)


    def create(self, **kwargs):
        return self.get_detail_object( {}, dehydrate_object=False)


class ListSubResource(ListResource):
    _cached_data = None

    def __init__(self,list_endpoint,schema_endpoint, **kwargs):
        self.list_endpoint = __SITE__ + list_endpoint
        self.schema_endpoint = schema_endpoint


class DetailResource(object):

    def __getattr__(self,attr_name, *args, **kwargs):
        if attr_name in self._list_object.schema['fields'].keys():
            self._update_object()
            return getattr(self, attr_name)
        else:
            raise AttributeError("'%s' does not exists in a '%s' object"%(attr_name, self.__class__.__name__))

    def __setattr__(self, attr_name, value):
        #TODO: validations
        if not hasattr(self, "_updated_data"):
            self.__dict__["_updated_data"] = {}
        if isinstance(value, list) and not isinstance(value, List):
            value = List(value)
        self.__dict__["_updated_data"][attr_name] = value
        self.__dict__[attr_name] = value

    def _update_object(self):
        #TODO Update the object in place
        obj = self._list_object.retrieve(self.id)

        #TODO: DIRTY STUFF REMOVE THESE
        for field_name in [name for name in dir(obj) if not name.startswith('_') and not name.startswith('json') and not name.startswith('get_file') and  name!="save" ]:
            self.__dict__[field_name] = getattr(obj, field_name)

    def _get_updated_data(self):
        """
        This method returns the updated data
         and also hydrates the fields before returning
        """
        if not hasattr(self, "_updated_data"):return {}

        updated_data = {}
        for field_name in self._updated_data.keys():
            if field_name in self._list_object.schema['fields'].keys():
                field_schema = self._list_object.schema['fields'][field_name]
                field_handler = get_field_handler(field_schema)
                hydrated_value = field_handler.hydrate(data=self._updated_data[field_name])
            else:
                hydrated_value = self._updated_data[field_name]
            updated_data[field_name] = hydrated_value
        return updated_data

    def save(self, **kwargs):
        list_uri = self._list_object.list_endpoint
        updated_data = self._get_updated_data()
        if not updated_data:
            return True

        if hasattr(self, "id"):
            #Update
            response = _request_handler.request("PATCH", "%s%s/"%(list_uri, self.id), [__USERNAME__,__API_KEY__], data=updated_data )
        else:
            #Creating new
            response = _request_handler.request("POST", "%s"%(list_uri), [__USERNAME__,__API_KEY__], data=updated_data )
            self.id = response['id']
            self.resource_uri = response['resource_uri']
        del self._updated_data
        return True


_request_handler = HttpRequest()

class Rbox(object):

    api_key = ""
    username = ""

    def __init__(self, **kwargs):
        #The below will the default parent class of the
        # ListResources and DetailResources
        self.default_list_class = kwargs.get("default_list_class", ListResource)
        self.default_detail_class = kwargs.get("default_detail_class", DetailResource)
        self.default_list_class.default_detail_class = self.default_detail_class

        #Should contain {"resource_name":ListClassForTheResource}
        self.resource_custom_list_class = kwargs.get("resource_custom_list_class", {})


    def getattr(self, attr_name):
        if not hasattr(self, "SITE") or not hasattr(self, "SCHEMA_DUMP_URI"):
            raise AttributeError("You seem to be accessing a resource without assigning the attribute 'SITE' and 'SCHEMA_DUMP_URI'.")

    def __setattr__(self, attr_name, value):
        self.__dict__[attr_name] = value
        if attr_name in ["SITE" , "SCHEMA_DUMP_URI"]:
            self._generate_schema()

        #Set the globals
        if attr_name in ["api_key" , "username", "SITE"]:
            global __API_KEY__
            global __USERNAME__
            global __SITE__
            __API_KEY__ = self.api_key
            __USERNAME__ = self.username
            __SITE__ = self.SITE

    def _generate_schema(self):
        if hasattr(self, "SITE") and hasattr(self, "SCHEMA_DUMP_URI"):
            #This condition makes sure that a schema dump is required
            self.__dict__['list_endpoint'] = "%s/api/v1/"%(self.SITE)
            self.__dict__['schema_endpoint'] = "/api/v1/"
            self.__dict__['schema'] =  get_schema(self.schema_endpoint, schema_dump_uri=self.SCHEMA_DUMP_URI)
            self.generate_list_resource_objects()

    def generate_list_resource_objects(self):
        for resource_name,resource_data in self.schema.iteritems():
            if resource_name in self.resource_custom_list_class.keys():
                list_class = self.resource_custom_list_class[resource_name]
            else:
                list_class = type(str(resource_name), (self.default_list_class,),{})
            list_class.list_endpoint = self.SITE+resource_data['list_endpoint']
            list_class.schema_endpoint = resource_data['schema']
            setattr(self,resource_name,list_class())


rbox = Rbox()
