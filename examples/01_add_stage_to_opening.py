import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

from rbox import rbox as api_client

api_client.SITE = "https://app.recruiterbox.com"
api_client.api_key = "your-api-key"
api_client.username = "demoaccount@recruiterbox.com"
api_client.SCHEMA_DUMP_URI = api_client.SITE+"/static/schema_dump.json"

openings = api_client.openings.all()
print openings
for opening in openings:
    new_stage = opening.stages.create()
    new_stage.name = 'new_stage'
    new_stage.save()
    
