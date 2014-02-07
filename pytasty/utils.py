import pytasty as api_client
from .field_handlers import get_field_handler

def dehydrate(detail_object):
    #TODO: DIRTY STUFF REMOVE THESE
    for field_name in [name for name in dir(detail_object) if not name.startswith('_') and not name.startswith("json") and  name not in ["save", "delete", "get_file"]]:
        field_schema = detail_object._list_object.schema['fields'].get(field_name)
        if not field_schema:
            detail_object.__dict__[field_name] = getattr(detail_object,field_name)
            continue

        field_handler = get_field_handler(field_schema)
        dehydrated_value = field_handler.dehydrate(getattr(detail_object,field_name), parent_obj=detail_object)
        detail_object.__dict__[field_name] = dehydrated_value
        #setattr(detail_object, field_name, dehydrated_value)

    return detail_object


def get_schema(schema_endpoint, from_dump = True, schema_dump_uri=None):
    if from_dump==True:
        if not hasattr(api_client.utils, "_schema_dump") and schema_dump_uri!=None:
            api_client.utils._schema_dump = api_client._request_handler.request("GET",\
                   schema_dump_uri )
        return api_client.utils._schema_dump[schema_endpoint]
    else:
        #TODO: Cache it and Get it from http
        pass