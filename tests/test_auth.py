

from .test_flasker import client 
import os
import json

def login(client):
        """Start with a blank database."""
        email = os.getenv("EMAIL")
        password = os.getenv("PASSWORD")

        rv = client.post('/auth/login', 
            data=json.dumps(dict(email=email,password=password)), 
            headers={"content-type":"application/json"},
            follow_redirects=True)
        assert b'Successfully logged in.' in rv.data

        data = json.loads(rv.data.decode("utf-8"))
        assert "access_token" in data

        token = data["access_token"]
        assert token[0] == "e"
        
        return token

def test_register(client):
        email = os.getenv("EMAIL")
        password = os.getenv("PASSWORD")
        name = "Ridwan Jalali"
        username="jalalirs"
        



def test_login(client):
        assert login(client)