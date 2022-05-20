import json

import requests
from flask import current_app

from app.utils import internal_err_resp, message


class Streamer:
    @staticmethod
    def capture_image(registry_key, camera, output_path):

        data = {
            "registry_key": registry_key,
            "camera": camera.con_to_json(),
            "output_path": output_path,
            "capture_type": "image",
        }
        resp = requests.post(
            f"{current_app.config['STREAMER_HOST']}/api/capture", data=json.dumps(data)
        )
        return resp

    @staticmethod
    def record_video(
        registry_key,
        camera,
        length,
        output_path,
    ):

        data = {
            "registry_key": registry_key,
            "camera": camera.con_to_json(),
            "length": length,
            "output_path": output_path,
            "capture_type": "video",
        }
        resp = requests.post(
            f"{current_app.config['STREAMER_HOST']}/api/capture", data=json.dumps(data)
        )
        return resp
