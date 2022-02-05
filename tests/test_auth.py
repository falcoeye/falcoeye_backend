import json


def login(client):
    """Start with a blank database."""
    data = dict(
        email="test@user.com",
        username="test.User",
        name="Test User",
        password="test1234",
    )

    rv = client.post(
        "/auth/login",
        data=json.dumps(dict(email=data["email"], password=data["password"])),
        headers={"content-type": "application/json"},
        follow_redirects=True,
    )
    assert b"Successfully logged in." in rv.data

    data = json.loads(rv.data.decode("utf-8"))
    assert "access_token" in data

    token = data["access_token"]
    assert token[0] == "e"

    return token


def test_login(client):
    assert login(client)
