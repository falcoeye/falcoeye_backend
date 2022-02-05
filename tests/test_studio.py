


from .test_flasker import client 
import os
import json
from .test_auth import login

def test_add_image(client):
    
    token = login(client)
    headers = {"X-API-KEY":token}
    try:
        rv = client.post("/api/media/add_image test1 1 test1 test1 1",headers=headers)
        data = json.loads(rv.data.decode("utf-8"))
        if "error_reason" in data:
            # in case name was taken
            assert data["error_reason"] == "name_taken"
            # delete first
            rv = client.post("/api/media/delete_image test1",headers=headers)
            data = json.loads(rv.data.decode("utf-8"))
            assert data["message"] == "Image has been deleted."

            # trying to add again
            rv = client.post("/api/media/add_image test1 1 test1 test1 1",headers=headers)
            data = json.loads(rv.data.decode("utf-8"))

        assert data["message"] == "Image has been added."
            
    except:
        raise


    

