import requests
from .exceptions import PyTastyNotFoundError, PyTastyError
import json
import time
import urlparse

FORMAT = "json"


class HttpRequest(object):

    params = {}  # {"format":FORMAT}
    headers = {"content-type": "application/json"}

    def _get_auth(self, api_key):
        if not api_key:
            return {}

    def request(self, method, uri, params=None, data=None, *args, **kwargs):
        uri, old_params = clean_url(uri)
        current_params = {}
        current_data = {}
        current_params.update(old_params)
        current_params.update(params or {})
        current_data.update(data or {})
        current_params.update(self.params)
        if hasattr(self, "username"):
            current_params.update({"username": self.username})
        if hasattr(self, "api_key"):
            current_params.update({"api_key": self.api_key})

        # start = time.time()
        # print method, uri, "============>     ",
        response = requests.request(
            method,
            uri,
            params=current_params,
            headers=self.headers,
            data=json.dumps(current_data))
        # print time.time() - start, "Seconds"
        return response_handler(response)


def clean_url(url):
    splits = url.split('?')
    cleaned_url = splits[0]
    if splits[1:]:
        params = {key: list(set(val))
                  for key, val in urlparse.parse_qs(splits[1]).items()}
    else:
        params = {}
    return cleaned_url, params


def response_handler(response):

    if response.status_code in [200, 201, 202]:
        return response.json()  # json.loads(response.content)
    elif response.status_code in [400]:
        raise PyTastyError("BAD REQUEST - %s" % (response.content))
    elif response.status_code in [401]:
        raise PyTastyError("User Unauthorized!!")
    elif response.status_code in [404]:
        raise PyTastyNotFoundError("404: Page Not Found!!")
    elif response.status_code in [500]:
        raise PyTastyError("There was an error in recruiterbox!")
