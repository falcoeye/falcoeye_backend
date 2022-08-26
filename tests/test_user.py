import json

from .utils import EMAIL, USERNAME, login_user


def test_user_details(client, db, user):
    resp = login_user(client)
    assert "access_token" in resp.json

    access_token = resp.json.get("access_token")

    headers = {"X-API-KEY": access_token}
    resp = client.get("/api/user/profile", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("user").get("username") == USERNAME
    assert resp.json.get("user").get("email") == EMAIL


def test_edit_user_details(client, db, user):
    resp = login_user(client)
    assert "access_token" in resp.json

    access_token = resp.json.get("access_token")
    data = {
        "email": "falcoeye-test-edited@falcoeye.io",
        "username": "falcoeye-test-edited",
        "name": "Falcoeye Test Edited",
    }
    headers = {"X-API-KEY": access_token}
    resp = client.get(
        "/api/user/edit",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json",
    )
    assert resp.status_code == 200

    resp = client.get("/api/user/profile", headers=headers)
    assert resp.json.get("user").get("username") == "falcoeye-test-edited"
    assert resp.json.get("user").get("email") == "falcoeye-test-edited@falcoeye.io"
    assert resp.json.get("user").get("name") == "Falcoeye Test Edited"
