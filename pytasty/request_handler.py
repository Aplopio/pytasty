import requests
from exceptions import PyTastyNotFoundError, PyTastyError
import json
import time

FORMAT = "json"

class RequestHandler(object):
    pass

class HttpRequest(RequestHandler):

    params ={} #{"format":FORMAT}
    headers = {"content-type":"application/json"}


    def _get_auth(self, api_key):
        if not api_key:
            return {}


    def request(self,method, uri, auth=[], params={}, data={}, *args, **kwargs):
        params.update(self.params)
        if auth:
            params.update({"username":auth[0], "api_key":auth[1]})

        start = time.time()
        #print method, uri, "============>     ",
        response = requests.request(method,uri, params=params,headers=self.headers, data=json.dumps(data))
        #print time.time() - start, "Seconds"
        return response_handler(response)


def response_handler(response):

    if response.status_code in [200, 201, 202]:
        return json.loads(response.content)
    elif response.status_code in [400]:
        raise PyTastyError("BAD REQUEST - %s"%(response.content))
    elif response.status_code in [401]:
        raise PyTastyError("User Unauthorized!!")
    elif response.status_code in [404]:
        raise PyTastyError("404: Page Not Found!!")
    elif response.status_code in [500]:
        raise PyTastyError("There was an error in recruiterbox!")
