
from .test_flasker import client 
import os
import json

def test_user_details(client):
    """Start with a blank database."""
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")


    rv = client.post('/auth/login', 
            data=json.dumps(dict(email=email,password=password)), 
            headers={"content-type":"application/json"},
            follow_redirects=True)
    
    data = json.loads(rv.data.decode("utf-8"))
    assert "access_token" in data

    token = data["access_token"]
    assert token[0] == "e"

    headers = {"X-API-KEY":token}
    rv = client.get("/api/user/profile",headers=headers)
    data = json.loads(rv.data.decode("utf-8"))
    print(data)
    assert data["user"]["username"] == "jalalirs"
    assert data["user"]["email"] == "jalalirsh@gmail.com"


