"""Shared functions and constants for unit tests."""

import json

import requests

EMAIL = "dummy_user@dummy.com"
USERNAME = "dummy.User"
PASSWORD = "test1234"
MANUFACTURER = "ViewIntoTheBlue"
STREAMER = "youtube"
CAMERA = {
    "name": "Harbour Village Bonaire Coral Reef",
    "status": "RUNNING",
    "url": "https://www.youtube.com/watch?v=tk-qJJbdOh4",
}


def register_user(test_client, email=EMAIL, password=PASSWORD, username=USERNAME):
    return test_client.post(
        "/auth/register",
        data=json.dumps(dict(email=email, password=password, username=username)),
        content_type="application/json",
    )


def login_user(test_client, email=EMAIL, password=PASSWORD, alt_host=None):
    return test_client.post(
        "/auth/login",
        data=json.dumps(dict(email=email, password=password)),
        content_type="application/json",
    )


def get_user(test_client, access_token):
    return test_client.get(
        "/api/user/profile", headers={"Authorization": f"X-API-TOKEN {access_token}"}
    )


def initialize_dev_environment(host):
    # registering
    resp = requests.post(
        f"http://{host}/auth/register",
        data=json.dumps(dict(email=EMAIL, password=PASSWORD, username=USERNAME)),
        headers={"Content-type": "application/json", "Host": host},
    )

    # loging
    resp = requests.post(
        f"http://{host}/auth/login",
        data=json.dumps(dict(email=EMAIL, password=PASSWORD)),
        headers={"Content-type": "application/json", "Host": host},
    )
    response_data = json.loads(resp.content.decode("utf-8"))
    assert "access_token" in response_data

    # access token
    access_token = response_data["access_token"]
    headers = {"X-API-KEY": access_token}

    # creating manufacturer
    request_data = {"name": MANUFACTURER}
    resp = requests.post(
        f"http://{host}/api/manufacturer/",
        data=json.dumps(request_data),
        headers={
            "Content-type": "application/json",
            "Host": host,
            "X-API-KEY": access_token,
        },
    )
    # retrieving manufacturers
    resp = requests.get(
        f"http://{host}/api/manufacturer/",
        headers={
            "Content-type": "application/json",
            "Host": host,
            "X-API-KEY": access_token,
        },
    )

    response_data = json.loads(resp.content.decode("utf-8"))
    assert "manufacturer" in response_data

    # finding ViewIntoTheBlue
    manufacturers = response_data["manufacturer"]
    mid = None
    for m in manufacturers:
        if m["name"] == MANUFACTURER:
            mid = m["id"]
            break

    # creating streamer
    request_data = {"name": STREAMER}
    resp = requests.post(
        f"http://{host}/api/streamer/",
        data=json.dumps(request_data),
        headers={
            "Content-type": "application/json",
            "Host": host,
            "X-API-KEY": access_token,
        },
    )
    # retrieving streamer
    resp = requests.get(
        f"http://{host}/api/streamer/",
        headers={
            "Content-type": "application/json",
            "Host": host,
            "X-API-KEY": access_token,
        },
    )
    response_data = json.loads(resp.content.decode("utf-8"))
    assert "streamer" in response_data

    # finding youtube
    streamers = response_data["streamer"]
    sid = None
    for s in streamers:
        if s["name"] == STREAMER:
            sid = s["id"]
            break

    # creating camera
    data = {
        "name": CAMERA["name"],
        "manufacturer_id": mid,
        "url": CAMERA["url"],
        "status": "RUNNING",
        "streamer_id": sid,
    }

    resp = requests.post(
        f"http://{host}/api/camera/",
        data=json.dumps(data),
        headers={
            "Content-type": "application/json",
            "Host": host,
            "X-API-KEY": access_token,
        },
    )

    # retrieving camera
    resp = requests.get(
        f"http://{host}/api/camera/",
        headers={
            "Content-type": "application/json",
            "Host": host,
            "X-API-KEY": access_token,
        },
    )
    response_data = json.loads(resp.content.decode("utf-8"))
    assert "camera" in response_data

    # finding our camera
    streamers = response_data["camera"]
    cid = None
    for c in streamers:
        if c["name"] == CAMERA["name"]:
            cid = c["id"]
            break

    return access_token, mid, sid, cid
