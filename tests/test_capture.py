import json
import logging
import threading
import time
from unittest import mock

from .utils import login_user


def mocked_streamer_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def response(self):
            return self.json_data, self.status_code

    return MockResponse({"status": True, "message": "Capture request initiated"}, 200)


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
        f"/api/capture/status/{reg_key}",
        headers={"X-API-KEY": access_token},
    )

    status = resp.json.get("capture_status")
    elapsed = 0
    while status == "STARTED":
        logging.info(status)
        time.sleep(sleep_time)
        if elapsed > time_before_kill:
            break

        resp = client.get(
            f"/api/capture/status/{reg_key}",
            headers={"X-API-KEY": access_token},
        )
        status = resp.json.get("capture_status")
        elapsed += sleep_time


def change_status(client, registry_key, admin_access_token, wait_before=2):
    time.sleep(wait_before)
    logging.info(f"Posting to change status for {registry_key}")

    res = client.post(
        f"/api/capture/status/{registry_key}",
        headers={
            "X-API-KEY": admin_access_token,
            "Content-type": "application/json",
        },
        data=json.dumps({"capture_status": "SUCCEEDED"}),
    )

    logging.info(res.json)


@mock.patch("app.api.capture.streamer.requests.post", side_effect=mocked_streamer_post)
def test_capture_image(mock_post, client, camera, streaming_admin):
    resp = login_user(client)
    assert "access_token" in resp.json
    access_token = resp.json.get("access_token")

    resp = login_user(client, streaming_admin["email"], streaming_admin["password"])
    assert "access_token" in resp.json
    admin_access_token = resp.json.get("access_token")

    registry_key = post_capture(client, camera.id, "image", access_token)

    th = threading.Thread(
        target=change_status, args=(client, registry_key, admin_access_token, 2)
    )
    th.start()

    time_before_kill = 100
    sleep_time = 3
    loop_until_finished(
        client, registry_key, time_before_kill, sleep_time, access_token
    )


@mock.patch("app.api.capture.streamer.requests.post", side_effect=mocked_streamer_post)
def test_capture_video(mock_post, client, camera, streaming_admin):
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
        length=10,
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
