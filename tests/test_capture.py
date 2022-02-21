import json
import os
import time

from .utils import initialize_dev_environment, login_user, register_user

DIR = os.path.dirname(os.path.realpath(__file__))
import signal

import requests

from config import DevelopmentConfig


def test_capture_image():
    backend_host = DevelopmentConfig.SERVER_NAME
    access_token, man_id, str_id, cam_id = initialize_dev_environment(backend_host)

    request_data = {"capture_type": "image", "camera_id": cam_id}
    headers = {
        "Content-type": "application/json",
        "Host": backend_host,
        "X-API-KEY": access_token,
    }
    resp = requests.post(
        f"http://{backend_host}/api/capture",
        data=json.dumps(request_data),
        headers=headers,
    )

    response_data = json.loads(resp.content.decode("utf-8"))
    assert "registry_key" in response_data

    rg_key = response_data["registry_key"]
    regdata = {"registry_key": rg_key}

    time.sleep(3)

    resp = requests.get(
        f"http://{backend_host}/api/capture/status/{rg_key}", headers=headers
    )

    response_data = json.loads(resp.content.decode("utf-8"))
    status = response_data["capture_status"]
    elapsed = 0
    while status != 7:
        time.sleep(3)
        if elapsed > 500:
            break

        resp = requests.get(
            f"http://{backend_host}/api/capture/status/{rg_key}", headers=headers
        )
        response_data = json.loads(resp.content.decode("utf-8"))
        status = response_data["capture_status"]
        print("Status is:", status)
        elapsed += 3

    assert status == 7
