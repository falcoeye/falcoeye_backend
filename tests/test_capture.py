import json
import os

from .conftest import client
from .test_auth import login


def test_capture_image(client):

    token = login(client)
    headers = {"X-API-KEY": token}

    data = {"capture_type": "image", "camera_id": 1}
    rv = client.post("/api/capture", data=json.dumps(data), headers=headers)
    data = json.loads(rv.data.decode("utf-8"))

    assert (
        data["message"] == "Image has been captured."
        or data["message"] == "Couldn't capture image. No stream found"
    )
    if data["message"] == "Couldn't capture image. No stream found":
        return

    tid = data["temprary_id"]
    image = data["image"]
    print(image)

    data = {
        "temprary_id": tid,
        "camera": 1,
        "notes": "test_notes",
        "tags": "test_tags",
        "workflow": 1,
    }

    rv = client.post("/api/media/image", headers=headers, data=json.dumps(data))
    data = json.loads(rv.data.decode("utf-8"))
    assert data["message"] == "Image has been added."
    media_id = data["image"]["id"]

    rv = client.get(f"/api/media/image/{media_id}", headers=headers)
    data = json.loads(rv.data.decode("utf-8"))
    print(data)
    assert data["message"] == "Image successfully retrieved."
    media_id = data["image"]["id"]

    rv = client.delete(
        "/api/media/image", headers=headers, data=json.dumps({"image_id": media_id})
    )
    data = json.loads(rv.data.decode("utf-8"))
    assert data["message"] == "Image has been deleted."
