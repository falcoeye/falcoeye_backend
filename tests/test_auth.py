

from .test_flasker import client 
import os
import json

def test_login(client):
    """Start with a blank database."""
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")


    rv = client.post('/auth/login', 
            data=json.dumps(dict(email=email,password=password)), 
            headers={"content-type":"application/json"},
            follow_redirects=True)
    assert b'Successfully logged in.' in rv.data