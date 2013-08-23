from request_handler import HttpRequest
from field_handlers import get_field_handler


class ListResource(object):

    def _generate_schema(self):
        self.schema = _request_handler.request("GET",self.schema_endpoint, [rbox.username,rbox.api_key])

    def _generate_detail_class(self):
        if not hasattr(self, "schema"):
            self._generate_schema()

        class_name = self.__class__.__name__
        if class_name.endswith("s"):
            class_name = class_name[:-1]
        class_name.capitalize()

        self._detail_class = type(class_name, (DetailResource,), {})

    def _get_detail_object(self, json_obj):
        if not hasattr(self, "_detail_class"):
            self._generate_detail_class()

        detail_object = self._detail_class()

        detail_object._list_object = self
        detail_object.json = json_obj
        for field_name, field_value in json_obj.iteritems():
            setattr(detail_object, field_name, field_value)

        return dehydrate(detail_object)

    def all(self, offset=0, limit=20, **kwargs):

        response_objects = _request_handler.request("GET", self.list_endpoint, [rbox.username,rbox.api_key] )

        #ONE HARDCODING
        for list_meta_name,list_meta_value in response_objects.pop("meta").iteritems():
            setattr(self, list_meta_name, list_meta_value)

        return [self._get_detail_object(obj) for obj in response_objects['objects']]

    def retrieve(self, id):
        response_object = _request_handler.request("GET", "%s%s/"%(self.list_endpoint, id), [rbox.username,rbox.api_key] )

        return self._get_detail_object(response_object)

    def create(self, data):
        pass


class DetailResource(object):

    def update(self, data):
        pass

    def __getattr__(self,attr_name, *args, **kwargs):
        if attr_name in self._list_object.schema['fields'].keys():
            #import ipdb;ipdb.set_trace()
            self._update_object()
            return getattr(self, attr_name)
        else:
            raise AttributeError("'%s' does not exists in a '%s' object"%(attr_name, self.__class__.__name__))


    def _update_object(self):
        #TODO Update the object in place
        obj = self._list_object.retrieve(self.id)

        #ANOTHER HARDCODING
        for field_name in [name for name in dir(obj) if not name.startswith('_')]:
            setattr(self, field_name, getattr(obj, field_name))


_request_handler = HttpRequest()

class Rbox(object):

    api_key = ""
    username = ""
    SITE = "https://app.recruiterbox.com"

    def __init__(self):
        self.list_endpoint = "%s/api/v1/"%(self.SITE)
        self.schema_endpoint = self.list_endpoint

        if not hasattr(self, "schema"):
            self._generate_schema()

    def _generate_schema(self):
        self.schema =  _request_handler.request("GET",self.schema_endpoint)
        _generate_list_resource_objects(self)

def _generate_list_resource_objects(rbox):
    for resource_name,resource_data in rbox.schema.iteritems():
        setattr(rbox,resource_name,type(str(resource_name), (ListResource,),\
             {"list_endpoint":rbox.SITE+resource_data['list_endpoint'], "schema_endpoint" : rbox.SITE+resource_data['schema'] })())


def dehydrate(detail_object):

    for field_name, field_schema in detail_object._list_object.schema['fields'].iteritems():
        field_handler = get_field_handler(field_schema)


rbox = Rbox()

rbox.api_key = "71831d7a84efc294ec1ab7251abac9c809c32c36"
rbox.username = "demoaccount@recruiterbox.com"
