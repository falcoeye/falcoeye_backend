import json
import os
import time

from . import utils as utils

DIR = os.path.dirname(os.path.realpath(__file__))
import signal

import requests

from config import DevelopmentConfig

backend_host = DevelopmentConfig.SERVER_NAME
headers = {
    "Content-type": "application/json",
    "Host": backend_host,
    "X-API-KEY": None,
}


def prepare():
    utils.register_user(backend_host)
    access_token = utils.login_user(backend_host)
    man_id = utils.create_manufacturer(backend_host, access_token)
    str_id = utils.create_streamer(backend_host, access_token)
    cam_id = utils.create_camera(backend_host, access_token, man_id, str_id)
    headers["X-API-KEY"] = access_token
    return man_id, str_id, cam_id


def post_capture(man_id, str_id, cam_id, ctype, **args):

    request_data = {"capture_type": ctype, "camera_id": cam_id}
    for k, v in args.items():
        request_data[k] = v

    resp = requests.post(
        f"http://{backend_host}/api/capture",
        data=json.dumps(request_data),
        headers=headers,
    )
    response_data = json.loads(resp.content.decode("utf-8"))
    assert "registry_key" in response_data
    rg_key = response_data["registry_key"]

    return rg_key


def loop_until_finished(reg_key, success_status, time_before_kill, sleep_time):

    time.sleep(success_status)

    resp = requests.get(
        f"http://{backend_host}/api/capture/status/{reg_key}", headers=headers
    )

    response_data = json.loads(resp.content.decode("utf-8"))
    status = response_data["capture_status"]
    elapsed = 0
    while status != success_status:
        time.sleep(sleep_time)
        if elapsed > time_before_kill:
            break

        resp = requests.get(
            f"http://{backend_host}/api/capture/status/{reg_key}", headers=headers
        )
        response_data = json.loads(resp.content.decode("utf-8"))
        status = response_data["capture_status"]
        print("Status is:", status)
        elapsed += sleep_time

    assert status == success_status


def test_capture_image():
    man_id, str_id, cam_id = prepare()
    registry_key = post_capture(man_id, str_id, cam_id, "image")

    time_before_kill = 100
    sleep_time = 3
    success_status = 7
    loop_until_finished(registry_key, success_status, time_before_kill, sleep_time)


def test_capture_video():
    man_id, str_id, cam_id = prepare()

    registry_key = post_capture(man_id, str_id, cam_id, "video", length=10)

    time_before_kill = 100
    sleep_time = 3
    success_status = 7
    loop_until_finished(registry_key, success_status, time_before_kill, sleep_time)
