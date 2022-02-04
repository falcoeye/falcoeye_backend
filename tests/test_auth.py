import json


def test_register_and_login(client):
    """Test Auth API registration and login"""
    # Test registration
    data = dict(
        email="test@user.com",
        username="test.User",
        name="Test User",
        password="test1234",
    )

    r = client.post(
        "/auth/register", data=json.dumps(data), content_type="application/json"
    )

    assert 201 == r.status_code

    r = client.post(
        "/auth/login",
        data=json.dumps(dict(email=data["email"], password=data["password"])),
        content_type="application/json",
    )
    assert b"Successfully logged in." in r.data
