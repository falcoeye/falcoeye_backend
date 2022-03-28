import json
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


def post_capture(client, man_id, str_id, cam_id, ctype, access_token, **args):
    request_data = {"capture_type": ctype, "camera_id": str(cam_id)}
    for k, v in args.items():
        request_data[k] = v

    resp = client.post(
        "/api/capture",
        data=json.dumps(request_data),
        content_type="application/json",
        headers={"X-API-KEY": access_token},
    )
    assert "registry_key" in resp.json
    rg_key = resp.json.get("registry_key")

    return rg_key


def loop_until_finished(
    client, reg_key, success_status, time_before_kill, sleep_time, access_token
):

    time.sleep(success_status)

    resp = client.get(
        f"/api/capture/status/{reg_key}",
        headers={"X-API-KEY": access_token},
    )

    status = resp.json.get("capture_status")
    elapsed = 0
    while status != success_status:
        time.sleep(sleep_time)
        if elapsed > time_before_kill:
            break

        resp = client.get(
            f"/api/capture/status/{reg_key}",
            headers={"X-API-KEY": access_token},
        )
        status = resp.json.get("capture_status")
        elapsed += sleep_time

    assert status == success_status


@mock.patch("app.api.capture.streamer.requests.post", side_effect=mocked_streamer_post)
def test_capture_image(mock_post, client, manufacturer, camera, streamer):
    resp = login_user(client)
    assert "access_token" in resp.json
    access_token = resp.json.get("access_token")

    registry_key = post_capture(
        client, manufacturer.id, streamer.id, camera.id, "image", access_token
    )

    payload = {
        "status": True,
        "message": "Image has been captured.",
        "registry_key": registry_key,
        "capture_status": "CAPTURED",
    }
    res = client.post(
        f"/api/capture/status/{registry_key}",
        headers={"X-API-KEY": access_token},
        content_type="application/json",
        data=json.dumps(payload),
    )
    assert res.status_code == 200

    time_before_kill = 100
    sleep_time = 3
    success_status = 7
    loop_until_finished(
        client, registry_key, success_status, time_before_kill, sleep_time, access_token
    )


@mock.patch("app.api.capture.streamer.requests.post", side_effect=mocked_streamer_post)
def test_capture_video(mock_post, client, manufacturer, camera, streamer):
    resp = login_user(client)
    assert "access_token" in resp.json
    access_token = resp.json.get("access_token")

    registry_key = post_capture(
        client,
        manufacturer.id,
        streamer.id,
        camera.id,
        "video",
        access_token,
        length=10,
    )

    payload = {
        "status": True,
        "message": "Stream has been recorded.",
        "registry_key": registry_key,
        "capture_status": "RECORDED",
    }
    res = client.post(
        f"/api/capture/status/{registry_key}",
        headers={"X-API-KEY": access_token},
        content_type="application/json",
        data=json.dumps(payload),
    )
    assert res.status_code == 200

    time_before_kill = 100
    sleep_time = 3
    success_status = 7
    loop_until_finished(
        client, registry_key, success_status, time_before_kill, sleep_time, access_token
    )
