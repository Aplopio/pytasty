import requests
from exceptions import RboxNotFoundError, RboxError
import json
import time

FORMAT = "json"

class RequestHandler(object):
    pass

class HttpRequest(RequestHandler):

    params = {
            "format":FORMAT
            }


    def _get_auth(self, api_key):
        if not api_key:
            return {}


    def request(self,method, uri, auth=[], params={}):
        #import ipdb;ipdb.set_trace()

        params.update(self.params)
        if auth:
            params.update({"username":auth[0], "api_key":auth[1]})

        #import ipdb;ipdb.set_trace()
        start = time.time()
        print uri
        response = requests.request(method,uri, params=params)
        print time.time() - start
        return response_handler(response)


def response_handler(response):

    if response.status_code in [200, 201, 202]:
        #import ipdb;ipdb.set_trace()
        return json.loads(response.content)
    elif response.status_code in [400]:
        raise RboxNotFoundError(response.content)
    elif response.status_code in [401]:
        raise RboxError("User Unauthorized!!")
    elif response.status_code in [500]:
        raise RboxError("There was an error in recruiterbox!")
