import json
import os
import time

from .conftest import client
from .test_auth import login


def test_capture_image(client):

    token = login(client)
    headers = {"X-API-KEY": token}

    data = {"capture_type": "image", "camera_id": 1}
    rv = client.post("/api/capture", data=json.dumps(data), headers=headers)
    data = json.loads(rv.data.decode("utf-8"))

    assert (
        data["message"] == "Capture image request been submitted."
        or data["message"] == "Couldn't capture image. No stream found"
    )
    if data["message"] == "Couldn't capture image. No stream found":
        return
    rg_key = data["registry_key"]
    regdata = {"registry_key": rg_key}

    time.sleep(3)

    rv = client.get("/api/capture/status", data=json.dumps(regdata), headers=headers)
    data = json.loads(rv.data.decode("utf-8"))
    status = data["capture_status"]
    elapsed = 0
    while status != 6:
        time.sleep(3)
        if elapsed > 60:
            break
        rv = client.get(
            "/api/capture/status", data=json.dumps(regdata), headers=headers
        )
        data = json.loads(rv.data.decode("utf-8"))
        status = data["capture_status"]
        print("Status is:", status)
        elapsed += 3

    assert status == 6
