import requests
from .exceptions import PyTastyNotFoundError, PyTastyError
import json
import time

FORMAT = "json"



class HttpRequest(object):

    params ={} #{"format":FORMAT}
    headers = {"content-type":"application/json"}


    def _get_auth(self, api_key):
        if not api_key:
            return {}


    def request(self,method, uri,  params={}, data={}, *args, **kwargs):
        params.update(self.params)
        if hasattr(self,"username"):
            params.update({"username":self.username})
        if hasattr(self,"api_key"):
            params.update({"api_key":self.api_key})


        start = time.time()
        #print method, uri, "============>     ",
        response = requests.request(method,uri, params=params,headers=self.headers, data=json.dumps(data))
        #print time.time() - start, "Seconds"
        return response_handler(response)


def response_handler(response):

    if response.status_code in [200, 201, 202]:
        return response.json() #json.loads(response.content)
    elif response.status_code in [400]:
        raise PyTastyError("BAD REQUEST - %s"%(response.content))
    elif response.status_code in [401]:
        raise PyTastyError("User Unauthorized!!")
    elif response.status_code in [404]:
        raise PyTastyNotFoundError("404: Page Not Found!!")
    elif response.status_code in [500]:
        raise PyTastyError("There was an error in recruiterbox!")
