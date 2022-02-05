import json
import os

from .conftest import client


def test_user_details(client):
    """Start with a blank database."""
    email = "test@user.com"
    password = "test1234"

    rv = client.post(
        "/auth/login",
        data=json.dumps(dict(email=email, password=password)),
        headers={"content-type": "application/json"},
        follow_redirects=True,
    )

    data = json.loads(rv.data.decode("utf-8"))
    assert "access_token" in data

    token = data["access_token"]
    assert token[0] == "e"

    headers = {"X-API-KEY": token}
    rv = client.get("/api/user/profile", headers=headers)
    data = json.loads(rv.data.decode("utf-8"))
    print(data)
    assert data["user"]["username"] == "test.User"
    assert data["user"]["email"] == "test@user.com"
