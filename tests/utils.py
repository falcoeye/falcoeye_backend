"""Shared functions and constants for unit tests."""
import json
import os

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
    # url
    if type(test_client) == str:
        resp = requests.post(
            f"http://{test_client}/auth/register",
            data=json.dumps(dict(email=EMAIL, password=PASSWORD, username=USERNAME)),
            headers={"Content-type": "application/json", "Host": test_client},
        )
    # active client
    else:
        return test_client.post(
            "/auth/register",
            data=json.dumps(dict(email=email, password=password, username=username)),
            content_type="application/json",
        )


def login_user(test_client, email=EMAIL, password=PASSWORD):
    if type(test_client) == str:
        resp = requests.post(
            f"http://{test_client}/auth/login",
            data=json.dumps(dict(email=EMAIL, password=PASSWORD)),
            headers={"Content-type": "application/json", "Host": test_client},
        )
        response_data = json.loads(resp.content.decode("utf-8"))
        # access token
        access_token = f'JWT {response_data["access_token"]}'
        return access_token
    else:

        resp = test_client.post(
            "/auth/login",
            data=json.dumps(dict(email=email, password=password)),
            content_type="application/json",
        )

        # to avoid lots of re-factoring in the moment
        class Resp:
            def __init__(self, resp):
                self.json = resp.json
                self.status_code = resp.status_code
                self.json["access_token"] = f'JWT {self.json["access_token"]}'

        return Resp(resp)


def get_user(test_client, access_token):
    return test_client.get(
        "/api/user/profile", headers={"Authorization": f"X-API-TOKEN {access_token}"}
    )


def create_manufacturer(test_client, access_token, name=MANUFACTURER):
    headers = {"X-API-KEY": access_token}
    if type(test_client) == str:
        # creating manufacturer
        request_data = {"name": name}
        resp = requests.post(
            f"http://{test_client}/api/manufacturer/",
            data=json.dumps(request_data),
            headers={
                "Content-type": "application/json",
                "Host": test_client,
                "X-API-KEY": access_token,
            },
        )
        # retrieving manufacturers
        resp = requests.get(
            f"http://{test_client}/api/manufacturer/",
            headers={
                "Content-type": "application/json",
                "Host": test_client,
                "X-API-KEY": access_token,
            },
        )
        response_data = json.loads(resp.content.decode("utf-8"))
        assert "manufacturer" in response_data

        # finding ViewIntoTheBlue
        manufacturers = response_data["manufacturer"]
        mid = None
        for m in manufacturers:
            if m["name"] == name:
                mid = m["id"]
                break
        return mid


def create_streamer(test_client, access_token, name=STREAMER):
    headers = {"X-API-KEY": access_token}
    if type(test_client) == str:
        # creating streamer
        request_data = {"name": name}
        resp = requests.post(
            f"http://{test_client}/api/streamer/",
            data=json.dumps(request_data),
            headers={
                "Content-type": "application/json",
                "Host": test_client,
                "X-API-KEY": access_token,
            },
        )
        # retrieving streamer
        resp = requests.get(
            f"http://{test_client}/api/streamer/",
            headers={
                "Content-type": "application/json",
                "Host": test_client,
                "X-API-KEY": access_token,
            },
        )
        response_data = json.loads(resp.content.decode("utf-8"))
        assert "streamer" in response_data

        # finding youtube
        streamers = response_data["streamer"]
        sid = None
        for s in streamers:
            if s["name"] == name:
                sid = s["id"]
                break
        return sid


def create_camera(test_client, access_token, manufacturer_id, streamer_id, name=CAMERA):
    headers = {"X-API-KEY": access_token}
    if type(test_client) == str:
        # creating camera
        data = {
            "name": CAMERA["name"],
            "manufacturer_id": manufacturer_id,
            "url": CAMERA["url"],
            "status": "RUNNING",
            "streamer_id": streamer_id,
        }

        resp = requests.post(
            f"http://{test_client}/api/camera/",
            data=json.dumps(data),
            headers={
                "Content-type": "application/json",
                "Host": test_client,
                "X-API-KEY": access_token,
            },
        )

        # retrieving camera
        resp = requests.get(
            f"http://{test_client}/api/camera/",
            headers={
                "Content-type": "application/json",
                "Host": test_client,
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
        return cid
