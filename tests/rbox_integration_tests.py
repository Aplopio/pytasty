from rbox import rbox as api_client
import unittest
import uuid


#'''
api_client.SITE = "http://demoaccount.rbox.com:8000"
api_client.api_key = "*******"
#'''

api_client.username = "demoaccount@recruiterbox.com"
api_client.SCHEMA_DUMP_URI = api_client.SITE+"/static/schema_dump.json"

def get_uuid():
    return uuid.uuid4().hex

class TestIntegration(unittest.TestCase):

    def test_get(self):
        assert api_client.candidates.all().next().id.isdigit()
        return

    def test_update(self):
        candidate = api_client.candidates.all().next()
        first_name = get_uuid()
        candidate.first_name = first_name
        assert candidate.save()
        candidate._update_object()
        assert candidate.first_name == first_name

    def test_create_retrieve(self):
        candidate = api_client.candidates.create()
        first_name = get_uuid()
        candidate.first_name = first_name
        assert candidate.save()
        candidate._update_object()
        candidate = api_client.candidates.retrieve(id=candidate.id)
        assert candidate.first_name == first_name
