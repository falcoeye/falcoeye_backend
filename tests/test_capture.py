import json
import logging
import os
import threading
import time
from unittest import mock

from app.utils import mkdir, put, rmtree

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


def post_capture(client, cam_id, ctype, access_token, **args):
    request_data = {"capture_type": ctype, "camera_id": str(cam_id)}
    for k, v in args.items():
        request_data[k] = v

    resp = client.post(
        "/api/capture",
        data=json.dumps(request_data),
        content_type="application/json",
        headers={"X-API-KEY": access_token},
    )
    logging.info(resp.json)
    assert "registry_key" in resp.json
    rg_key = resp.json.get("registry_key")

    return rg_key


def loop_until_finished(client, reg_key, time_before_kill, sleep_time, access_token):

    resp = client.get(
        f"/api/capture/{reg_key}",
        headers={"X-API-KEY": access_token},
    )

    respjson = resp.json
    status = respjson.get("capture_status")
    elapsed = 0
    while status == "STARTED":
        logging.info(status)
        time.sleep(sleep_time)
        if elapsed > time_before_kill:
            break

        resp = client.get(
            f"/api/capture/{reg_key}",
            headers={"X-API-KEY": access_token},
        )
        respjson = resp.json
        status = respjson.get("capture_status")
        elapsed += sleep_time
    return respjson


def change_status(client, registry_key, admin_access_token, wait_before=2):
    time.sleep(wait_before)
    logging.info(f"Posting to change status for {registry_key}")

    res = client.post(
        f"/api/capture/{registry_key}",
        headers={
            "X-API-KEY": admin_access_token,
            "Content-type": "application/json",
        },
        data=json.dumps({"capture_status": "SUCCEEDED"}),
    )

    logging.info(res.json)


@mock.patch("app.api.capture.streamer.requests.post", side_effect=mocked_streamer_post)
def test_capture_image(mock_post, app, client, camera, streaming_admin):
    resp = login_user(client)
    assert "access_token" in resp.json
    access_token = resp.json.get("access_token")
    logging.info("Access token: " + access_token)

    resp = login_user(client, streaming_admin["email"], streaming_admin["password"])
    assert "access_token" in resp.json
    admin_access_token = resp.json.get("access_token")

    logging.info("Admin access token:" + admin_access_token)
    registry_key = post_capture(client, camera.id, "image", access_token)

    logging.info("Registry key: " + registry_key)

    th = threading.Thread(
        target=change_status, args=(client, registry_key, admin_access_token, 2)
    )
    th.start()

    time_before_kill = 100
    sleep_time = 3
    resp = loop_until_finished(
        client, registry_key, time_before_kill, sleep_time, access_token
    )

    image_info = {
        "camera_id": str(camera.id),
        "tags": "DummyTags",
        "note": "DummyNote",
        "registry_key": registry_key,
    }

    user_id = get_user_id(client, access_token)
    logging.info(f"User id: {user_id}")
    user_img_dir = f"{app.config['TEMPORARY_DATA_PATH']}/{user_id}/images/"
    logging.info(f"User image directory: {user_img_dir}")
    mkdir(user_img_dir)
    logging.info(f"Directory created? {os.path.exists(user_img_dir)}")
    logging.info(
        f"Copying: {basedir}/media/fish.jpg to {user_img_dir}/{registry_key}.jpg"
    )

    put(f"{basedir}/media/fish.jpg", f"{user_img_dir}/{registry_key}.jpg")
    logging.info(f"Creating thumbnail {user_img_dir}/{registry_key}_120.jpg")
    put(f"{basedir}/media/fish.jpg", f"{user_img_dir}/{registry_key}_120.jpg")

    resp = client.post(
        "/api/media/image",
        data=json.dumps(image_info),
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


@mock.patch("app.api.capture.streamer.requests.post", side_effect=mocked_streamer_post)
def test_capture_video(mock_post, app, client, camera, streaming_admin):
    resp = login_user(client)
    assert "access_token" in resp.json
    access_token = resp.json.get("access_token")

    resp = login_user(client, streaming_admin["email"], streaming_admin["password"])
    assert "access_token" in resp.json
    admin_access_token = resp.json.get("access_token")

    registry_key = post_capture(
        client,
        camera.id,
        "video",
        access_token,
        length=1,
    )

    th = threading.Thread(
        target=change_status, args=(client, registry_key, admin_access_token, 2)
    )
    th.start()

    time_before_kill = 100
    sleep_time = 3
    loop_until_finished(
        client, registry_key, time_before_kill, sleep_time, access_token
    )

    video_info = {
        "camera_id": str(camera.id),
        "tags": "DummyTags",
        "note": "DummyNote",
        "registry_key": registry_key,
    }

    user_id = get_user_id(client, access_token)
    logging.info(f"User id: {user_id}")
    user_vid_dir = f"{app.config['TEMPORARY_DATA_PATH']}/{user_id}/videos/"
    logging.info(f"User video directory: {user_vid_dir}")
    mkdir(user_vid_dir)
    logging.info(f"Directory created? {os.path.exists(user_vid_dir)}")
    logging.info(
        f"Copying: {basedir}/media/arabian_angelfish_short.mp4 to {user_vid_dir}/{registry_key}.mp4"
    )

    # Currently only supporting mp4
    put(
        f"{basedir}/media/arabian_angelfish_short.mp4",
        f"{user_vid_dir}/{registry_key}.mp4",
    )

    logging.info("Creating thumbnail")
    put(f"{basedir}/media/fish.jpg", f"{user_vid_dir}/{registry_key}_120.jpg")

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


@mock.patch("app.api.capture.streamer.requests.post", side_effect=mocked_streamer_post)
def test_delete_caputre(mock_post, app, client, camera, streaming_admin):
    resp = login_user(client)
    assert "access_token" in resp.json
    access_token = resp.json.get("access_token")

    resp = login_user(client, streaming_admin["email"], streaming_admin["password"])
    assert "access_token" in resp.json
    admin_access_token = resp.json.get("access_token")

    registry_key = post_capture(
        client,
        camera.id,
        "video",
        access_token,
        length=1,
    )

    th = threading.Thread(
        target=change_status, args=(client, registry_key, admin_access_token, 2)
    )
    th.start()

    time_before_kill = 100
    sleep_time = 3
    loop_until_finished(
        client, registry_key, time_before_kill, sleep_time, access_token
    )

    user_id = get_user_id(client, access_token)
    logging.info(f"User id: {user_id}")
    user_vid_dir = f"{app.config['TEMPORARY_DATA_PATH']}/{user_id}/videos/"
    logging.info(f"User video directory: {user_vid_dir}")
    mkdir(user_vid_dir)
    logging.info(f"Directory created? {os.path.exists(user_vid_dir)}")
    logging.info(
        f"Copying: {basedir}/media/arabian_angelfish_short.mp4 to {user_vid_dir}/{registry_key}.mp4"
    )

    # Currently only supporting mp4
    put(
        f"{basedir}/media/arabian_angelfish_short.mp4",
        f"{user_vid_dir}/{registry_key}.mp4",
    )

    logging.info("Creating thumbnail")
    put(f"{basedir}/media/fish.jpg", f"{user_vid_dir}/{registry_key}_120.jpg")

    resp = client.delete(
        f"/api/capture/{registry_key}",
        headers={
            "X-API-KEY": access_token,
            "Content-type": "application/json",
        },
    )

    assert resp.status_code == 200

    user_temp_dir = f"{app.config['TEMPORARY_DATA_PATH']}/{user_id}"
    rmtree(user_temp_dir)


@mock.patch("app.api.capture.streamer.requests.post", side_effect=mocked_streamer_post)
def test_delete_caputre_by_admin(mock_post, app, client, camera, streaming_admin):
    resp = login_user(client)
    assert "access_token" in resp.json
    access_token = resp.json.get("access_token")

    resp = login_user(client, streaming_admin["email"], streaming_admin["password"])
    assert "access_token" in resp.json
    admin_access_token = resp.json.get("access_token")

    registry_key = post_capture(
        client,
        camera.id,
        "video",
        access_token,
        length=1,
    )

    th = threading.Thread(
        target=change_status, args=(client, registry_key, admin_access_token, 2)
    )
    th.start()

    time_before_kill = 100
    sleep_time = 3
    loop_until_finished(
        client, registry_key, time_before_kill, sleep_time, access_token
    )

    user_id = get_user_id(client, access_token)
    logging.info(f"User id: {user_id}")
    user_vid_dir = f"{app.config['TEMPORARY_DATA_PATH']}/{user_id}/videos/"
    logging.info(f"User video directory: {user_vid_dir}")
    mkdir(user_vid_dir)
    logging.info(f"Directory created? {os.path.exists(user_vid_dir)}")
    logging.info(
        f"Copying: {basedir}/media/arabian_angelfish_short.mp4 to {user_vid_dir}/{registry_key}.mp4"
    )

    # Currently only supporting mp4
    put(
        f"{basedir}/media/arabian_angelfish_short.mp4",
        f"{user_vid_dir}/{registry_key}.mp4",
    )

    logging.info("Creating thumbnail")
    put(f"{basedir}/media/fish.jpg", f"{user_vid_dir}/{registry_key}_120.jpg")

    resp = client.delete(
        f"/api/capture/{registry_key}",
        headers={
            "X-API-KEY": admin_access_token,
            "Content-type": "application/json",
        },
    )

    assert resp.status_code == 200

    user_temp_dir = f"{app.config['TEMPORARY_DATA_PATH']}/{user_id}"
    rmtree(user_temp_dir)
