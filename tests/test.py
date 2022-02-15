import json
import os
import time

import requests

link = "http://127.0.0.1:8000"


def login():
    """Start with a blank database."""
    data = dict(
        email="test@user.com",
        username="test.User",
        name="Test User",
        password="test1234",
    )

    rv = requests.post(
        f"{link}/auth/login",
        data=json.dumps(dict(email=data["email"], password=data["password"])),
        headers={"content-type": "application/json"},
    )
    data = json.loads(rv.content.decode("utf-8"))
    assert "Successfully logged in." == data["message"]

    assert "access_token" in data

    token = data["access_token"]
    assert token[0] == "e"

    return token


def test_capture_image():

    token = login()
    headers = {"X-API-KEY": token}
    data = {"capture_type": "image", "camera_id": 1}
    rv = requests.post(f"{link}/api/capture", data=json.dumps(data), headers=headers)

    data = json.loads(rv.content.decode("utf-8"))

    assert (
        data["message"] == "Capture image request been submitted."
        or data["message"] == "Couldn't capture image. No stream found"
    )
    if data["message"] == "Couldn't capture image. No stream found":
        return
    rg_key = data["registry_key"]
    regdata = {"registry_key": rg_key}

    time.sleep(3)

    rv = requests.get(
        f"{link}/api/capture/status", data=json.dumps(regdata), headers=headers
    )
    data = json.loads(rv.content.decode("utf-8"))
    status = data["capture_status"]
    elapsed = 0
    while status != 7:
        time.sleep(3)
        if elapsed > 60:
            break
        rv = requests.get(
            f"{link}/api/capture/status", data=json.dumps(regdata), headers=headers
        )
        data = json.loads(rv.content.decode("utf-8"))
        status = data["capture_status"]
        elapsed += 3


def test_record_video():

    token = login()
    headers = {"X-API-KEY": token}
    data = {"capture_type": "video", "camera_id": 1, "length": 10}
    rv = requests.post(f"{link}/api/capture", data=json.dumps(data), headers=headers)

    data = json.loads(rv.content.decode("utf-8"))

    assert (
        data["message"] == "Recording video request been submitted."
        or data["message"] == "Couldn't record video. No stream found"
    )
    if data["message"] == "Couldn't record video. No stream found":
        return
    rg_key = data["registry_key"]
    regdata = {"registry_key": rg_key}

    time.sleep(3)

    rv = requests.get(
        f"{link}/api/capture/status", data=json.dumps(regdata), headers=headers
    )
    data = json.loads(rv.content.decode("utf-8"))
    status = data["capture_status"]
    elapsed = 0
    while status != 7:
        time.sleep(3)
        if elapsed > 60:
            break
        rv = requests.get(
            f"{link}/api/capture/status", data=json.dumps(regdata), headers=headers
        )
        data = json.loads(rv.content.decode("utf-8"))
        status = data["capture_status"]
        print("Status is:", status)
        elapsed += 3


# test_capture_image()
test_record_video()
