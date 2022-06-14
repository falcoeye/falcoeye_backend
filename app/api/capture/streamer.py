import json

import requests
from falcoeye_kubernetes import FalcoServingKube
from flask import current_app

from app.utils import internal_err_resp, message


class Streamer:
    streaming_kube = FalcoServingKube("falcoeye-streaming")

    @staticmethod
    def capture_image(registry_key, camera, output_path):

        data = {
            "registry_key": registry_key,
            "camera": camera.con_to_json(),
            "output_path": output_path,
            "capture_type": "image",
        }
        streaming_server = Streamer.streaming_kube.kube.get_service_address()
        resp = requests.post(f"{streaming_server}/api/capture", data=json.dumps(data))
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
