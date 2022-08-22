import json

import requests
from flask import current_app


class Streamer:
    @staticmethod
    def capture_image(registry_key, camera, output_path):
        streaming_service = current_app.config["STREAMER_HOST"]
        data = {
            "registry_key": registry_key,
            "camera": camera.con_to_json(),
            "output_path": output_path,
            "capture_type": "image",
        }
        resp = requests.post(f"{streaming_service}/api/capture", data=json.dumps(data))
        return resp

    @staticmethod
    def record_video(
        registry_key,
        camera,
        length,
        output_path,
    ):
        streaming_service = current_app.config["STREAMER_HOST"]
        data = {
            "registry_key": registry_key,
            "camera": camera.con_to_json(),
            "length": length,
            "output_path": output_path,
            "capture_type": "video",
        }
        resp = requests.post(f"{streaming_service}/api/capture", data=json.dumps(data))
        return resp

    @staticmethod
    def generate_thumbnail(video_file, output_path):
        streaming_service = current_app.config["STREAMER_HOST"]
        data = {
            "video_file": video_file,
            "output_path": output_path,
            "capture_type": "thumbnail",
        }
        resp = requests.post(f"{streaming_service}/api/capture", data=json.dumps(data))
        return resp
