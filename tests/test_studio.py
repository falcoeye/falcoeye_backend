from .utils import login_user


def test_add_image(client, db, user):
    resp = login_user(client)
    assert "access_token" in resp.json

    access_token = resp.json.get("access_token")
    headers = {"X-API-KEY": access_token}

    resp = client.post("/api/media/add_image test1 1 test1 test1 1", headers=headers)
    assert resp.json.get("message") == "Image has been added."

    resp = client.post("/api/media/delete_image test1", headers=headers)
    assert resp.json.get("message") == "Image has been deleted."
