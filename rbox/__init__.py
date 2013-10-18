from request_handler import HttpRequest
import time
import requests
from StringIO import StringIO
from utils import generate_list_resource_objects, dehydrate, get_schema

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

        setattr(rbox, class_name,type(class_name, (DetailResource,), {"_list_object":self}) )
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

        response_objects = _request_handler.request("GET", self.list_endpoint, [rbox.username,rbox.api_key] )
        next_url = response_objects['meta']['next']
        objects = response_objects['objects']

        while True:
            for obj in objects:
                yield self.get_detail_object(obj)
            if next_url:
                response_objects = _request_handler.request("GET", rbox.SITE + next_url, [rbox.username,rbox.api_key] )
                next_url = response_objects['meta']['next']
                objects = response_objects['objects']
            else:
                break

    def get(self, offset=0, limit=20, **kwargs):
        response_objects = _request_handler.request("GET", self.list_endpoint, [rbox.username,rbox.api_key] )

        #ONE HARDCODING
        for list_meta_name,list_meta_value in response_objects.pop("meta").iteritems():
            setattr(self, list_meta_name, list_meta_value)

        return [self.get_detail_object(obj) for obj in response_objects['objects']]


    def retrieve(self, id):
        response_object = _request_handler.request("GET", "%s%s/"%(self.list_endpoint, id), [rbox.username,rbox.api_key] )

        return self.get_detail_object(response_object)


    def create(self, **kwargs):
        return self._generate_detail_class()()

class ListDocResource(ListResource):

    def _generate_detail_class(self):
        if not hasattr(self, "schema"):
            self._generate_schema()

        class_name = self.__class__.__name__
        if class_name.endswith("s"):
            class_name = class_name[:-1]
        class_name = class_name.capitalize()

        setattr(rbox, class_name,type(class_name, (DetailDocResource,), {}) )
        self._detail_class = getattr(rbox, class_name)

    def all(self, **kwargs):
        return []

class ListSubResource(ListResource):
    _cached_data = None

    def __init__(self,list_endpoint,schema_endpoint, **kwargs):
        self.list_endpoint = rbox.SITE + list_endpoint
        self.schema_endpoint = rbox.SITE + schema_endpoint


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
        self.__dict__["_updated_data"][attr_name] = value
        self.__dict__[attr_name] = value

    def _update_object(self):
        #TODO Update the object in place
        obj = self._list_object.retrieve(self.id)

        #TODO: DIRTY STUFF REMOVE THESE
        for field_name in [name for name in dir(obj) if not name.startswith('_') and not name.startswith('json') and not name.startswith('get_file') and  name!="save" ]:

            self.__dict__[field_name] = getattr(obj, field_name)

    def save(self, **kwargs):
        list_uri = self._list_object.list_endpoint
        if hasattr(self, "id"):
            #Update
            response = _request_handler.request("PATCH", "%s%s/"%(list_uri, self.id), [rbox.username,rbox.api_key], data=self._updated_data )

        else:
            #Creating new
            response = _request_handler.request("POST", "%s"%(list_uri), [rbox.username,rbox.api_key], data=self._updated_data )
            self.id = response['id']

        del self._updated_data
        return True


class DetailDocResource(DetailResource):
    """
    This is a special case
    """

    def get_file(self):
        self._update_object()
        response = requests.get(rbox.SITE + self.location)
        response = requests.get(response.content)
        buff = StringIO()
        buff.content_type = response.headers['content-type']
        buff.name = self.filename
        buff.write(response.content)
        buff.seek(0)
        #buff.close()
        return buff

_request_handler = HttpRequest()

class Rbox(object):

    api_key = ""
    username = ""

    def getattr(self, attr_name):
        if not hasattr(self, "SITE") or not hasattr(self, "SCHEMA_DUMP_URI"):
            raise AttributeError("You seem to be accessing a resource without assigning the attribute 'SITE' and 'SCHEMA_DUMP_URI'.")

    def __setattr__(self, attr_name, value):
        self.__dict__[attr_name] = value
        if attr_name in ["SITE" , "SCHEMA_DUMP_URI"]:
            self._generate_schema()

    def _generate_schema(self):
        if hasattr(self, "SITE") and hasattr(self, "SCHEMA_DUMP_URI"):
            #This condition makes sure that a schema dump is required
            self.__dict__['list_endpoint'] = "%s/api/v1/"%(self.SITE)
            self.__dict__['schema_endpoint'] = "/api/v1/"
            self.__dict__['schema'] =  get_schema(self.schema_endpoint)
            generate_list_resource_objects(self)


rbox = Rbox()
