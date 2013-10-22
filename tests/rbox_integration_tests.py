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
        self.assertRaises(AttributeError, candidate.accessible_to.append, user)
        candidate.accessible_to = candidate.accessible_to + [user]
        assert candidate.save()
        candidate._update_object()
        new_accessible_ids = [accessible_user.id for accessible_user in candidate.accessible_to ]
        assert user.id in new_accessible_ids
        for accessible_user_id in accessible_to_ids:assert accessible_user_id in new_accessible_ids

        ####This below line tests __setattr__ for change of list type
        candidate.accessible_to = [user]
        self.assertRaises(AttributeError, candidate.accessible_to.append, 12)


import rbox as api

class TestListResource(api.ListResource):
    pass
class TestDetailResource(api.DetailResource):
    pass
class TestDetailCandidateResource(api.DetailResource):
    pass
class TestListDocResource(api.DetailResource):
    pass



class TestCase(unittest.TestCase):

    def test_setting_default_classes(self):
        cust_api_client = api.Rbox(default_list_class=TestListResource,default_detail_class=TestDetailResource, resource_custom_list_class={"docs":TestListDocResource} )
        cust_api_client.SITE = api_client.SITE
        cust_api_client.api_key = api_client.api_key
        cust_api_client.username = api_client.username
        cust_api_client.SCHEMA_DUMP_URI = api_client.SCHEMA_DUMP_URI
        assert isinstance ( cust_api_client.candidates, TestListResource)
        assert isinstance ( cust_api_client.candidates.create(), TestDetailResource)
        cust_api_client.candidates._detail_class = TestDetailCandidateResource
        assert isinstance ( cust_api_client.candidates.create(), TestDetailCandidateResource)
        assert isinstance ( cust_api_client.docs, TestListDocResource)