import rbox as api_client
from field_handlers import get_field_handler

def generate_list_resource_objects(rbox):
    for resource_name,resource_data in rbox.schema.iteritems():
        if resource_name == "docs":
            setattr(rbox,resource_name,type(str(resource_name), (api_client.ListDocResource,),\
                {"list_endpoint":rbox.SITE+resource_data['list_endpoint'], "schema_endpoint" : resource_data['schema'] })())
        else:
            setattr(rbox,resource_name,type(str(resource_name), (api_client.ListResource,),\
                {"list_endpoint":rbox.SITE+resource_data['list_endpoint'], "schema_endpoint" : resource_data['schema'] })())



def dehydrate(detail_object):
    #TODO: DIRTY STUFF REMOVE THESE
    for field_name in [name for name in dir(detail_object) if not name.startswith('_') and not name.startswith("json") and not name.startswith('get_file') and  name!="save"]:

        field_schema = detail_object._list_object.schema['fields'][field_name]
        field_handler = get_field_handler(field_schema)
        dehydrated_value = field_handler.dehydrate(getattr(detail_object,field_name), parent_obj=detail_object)
        detail_object.__dict__[field_name] = dehydrated_value
        #setattr(detail_object, field_name, dehydrated_value)

    return detail_object


def get_schema(schema_endpoint, from_dump = True):
    if from_dump==True:
        if not hasattr(api_client.utils, "_schema_dump"):
            api_client.utils._schema_dump = api_client._request_handler.request("GET",\
                    api_client.rbox.SCHEMA_DUMP_URI)
        return api_client.utils._schema_dump[schema_endpoint]
    else:
        #TODO: Cache it and Get it from http
        pass