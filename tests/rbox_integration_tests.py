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

    def test_create_get_subresource(self):
        candidate = api_client.candidates.create()
        first_name = get_uuid()
        candidate.first_name = first_name
        candidate.email = "xxx@example.com"
        assert candidate.save()
        candidate._update_object()
        cand_message = candidate.candidate_messages.create()

        cand_message.subject = "TEST"
        cand_message.message = "TEST MESSAGE"
        assert cand_message.save()
        for candidate_message in candidate.candidate_messages.all():
            assert candidate_message.id == cand_message.id

    def test_update_get_relatedfields(self):
        candidate = api_client.candidates.create()
        first_name = get_uuid()
        candidate.first_name = first_name
        candidate.email = "xxx@example.com"
        assert candidate.save()
        candidate._update_object()

        user = api_client.users.create()
        user.user_type = "privileged"
        user.email = "%s@example.com"%(get_uuid())
        user.password = get_uuid()
        user.name = get_uuid()
        assert user.save()
        accessible_to_ids = [accessible_user.id for accessible_user in candidate.accessible_to ]
        candidate.accessible_to = candidate.accessible_to + [user]
        assert candidate.save()
        candidate._update_object()
        new_accessible_ids = [accessible_user.id for accessible_user in candidate.accessible_to ]
        assert user.id in new_accessible_ids
        for accessible_user_id in accessible_to_ids:assert accessible_user_id in new_accessible_ids