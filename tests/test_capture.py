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
    print(data)
    assert (
        data["message"] == "Capture image request been submitted."
        or data["message"] == "Couldn't capture image. No stream found"
    )
    if data["message"] == "Couldn't capture image. No stream found":
        return

    tid = data["registry_key"]
    print(tid)
