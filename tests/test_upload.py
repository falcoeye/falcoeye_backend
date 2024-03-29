import json
import logging
import os
from unittest import mock

from app.utils import rmtree

from .utils import login_user

basedir = os.path.abspath(os.path.dirname(__file__))


def mocked_streamer_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def response(self):
            return self.json_data, self.status_code

    return MockResponse({"status": True, "message": "Capture request initiated"}, 200)


def get_user_id(client, access_token):
    headers = {"X-API-KEY": access_token}
    resp = client.get("/api/user/profile", headers=headers)
    assert resp.status_code == 200
    respjson = resp.json
    logging.info(f"User profile {respjson}")
    return str(respjson.get("user").get("id"))


@mock.patch("app.api.capture.streamer.requests.post", side_effect=mocked_streamer_post)
def test_upload_video(mock_post, app, client, user):
    resp = login_user(client)
    assert "access_token" in resp.json
    access_token = resp.json.get("access_token")

    filename = f"{basedir}/media/arabian_angelfish_short.mp4"
    files = {"file": open(filename, "rb")}

    resp = client.post(
        "/api/upload",
        headers={"X-API-KEY": access_token},
        data=files,
        content_type="multipart/form-data",
    )

    assert resp.status_code == 200
    assert "registry_key" in resp.json

    video_info = {
        "camera_id": None,
        "tags": "DummyTags",
        "note": "DummyNote",
        "registry_key": resp.json["registry_key"],
    }

    user_id = get_user_id(client, access_token)
    logging.info(f"User id: {user_id}")

    resp = client.post(
        "/api/media/video",
        data=json.dumps(video_info),
        headers={
            "X-API-KEY": access_token,
            "Content-type": "application/json",
        },
    )

    assert resp.status_code == 201
    user_temp_dir = f"{app.config['TEMPORARY_DATA_PATH']}/{user_id}"
    user_asset_dir = f"{app.config['USER_ASSETS']}/{user_id}"
    rmtree(user_temp_dir)
    rmtree(user_asset_dir)


def test_upload_image(app, client, user):
    resp = login_user(client)
    assert "access_token" in resp.json
    access_token = resp.json.get("access_token")

    filename = f"{basedir}/media/fish.jpg"
    files = {"file": open(filename, "rb")}

    resp = client.post(
        "/api/upload",
        headers={"X-API-KEY": access_token},
        data=files,
        content_type="multipart/form-data",
    )

    assert resp.status_code == 200
    assert "registry_key" in resp.json

    video_info = {
        "camera_id": None,
        "tags": "DummyTags",
        "note": "DummyNote",
        "registry_key": resp.json["registry_key"],
    }

    user_id = get_user_id(client, access_token)
    logging.info(f"User id: {user_id}")

    resp = client.post(
        "/api/media/video",
        data=json.dumps(video_info),
        headers={
            "X-API-KEY": access_token,
            "Content-type": "application/json",
        },
    )

    assert resp.status_code == 201
    user_temp_dir = f"{app.config['TEMPORARY_DATA_PATH']}/{user_id}"
    user_asset_dir = f"{app.config['USER_ASSETS']}/{user_id}"
    rmtree(user_temp_dir)
    rmtree(user_asset_dir)
