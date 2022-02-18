import json
import os

from .conftest import client
from .test_auth import login
from .utils import login_user


def test_add_image(client, user, harbourcamera):
    resp = login_user(client)
    assert "access_token" in resp.json

    access_token = resp.json.get("access_token")
    headers = {"X-API-KEY": access_token}
    data = {
        "camera_id": str(harbourcamera.id),
        "note": "test_notes",
        "tags": "test_tags",
    }

    resp = client.post(
        "/api/media/image",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json",
    )

    assert resp.status_code == 201
    assert resp.json.get("message") == "Image has been added"

    resp = client.get("/api/media/", headers=headers)
    assert resp.json.get("media")[0].get("camera_id") == str(harbourcamera.id)
    assert resp.status_code == 200
    assert resp.json.get("message") == "User data sent"

    # print(resp.json.get("image")[0])
