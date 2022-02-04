import json
import os


def test_login(client):
    """Start with a blank database."""
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    rv = client.post(
        "/auth/login",
        data=json.dumps(dict(email=email, password=password)),
        content_type="application/json",
    )
    assert b"Successfully logged in." in rv.data
