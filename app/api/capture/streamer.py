import json
import logging
import os

import requests
from flask import current_app

from app.utils import get_service, mkdir


class Streamer:
    @staticmethod
    def capture_image(registry_key, camera, output_path):
        streaming_service = get_service("falcoeye-streaming")
        output_dir = os.path.dirname(output_path)
        mkdir(output_dir)
        data = {
            "type": "image",
            "registry_key": registry_key,
            "camera": camera.con_to_json(),
            "output_path": output_path,
            "output_dir": output_dir,
        }
        capture_file = f"{output_dir}/capture.json"
        with open(capture_file, "w") as f:
            f.write(json.dumps(data))
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        resp = requests.post(
            f"{streaming_service}/api/capture",
            json={"capture_file": capture_file},
            headers=headers,
        )
        return resp

    @staticmethod
    def record_video(
        registry_key,
        camera,
        length,
        output_path,
    ):
        streaming_service = get_service("falcoeye-streaming")
        output_dir = os.path.dirname(output_path)
        mkdir(output_dir)
        data = {
            "type": "video",
            "registry_key": registry_key,
            "camera": camera.con_to_json(),
            "length": length,
            "output_dir": output_dir,
            "output_path": output_path,
        }
        capture_file = f"{output_dir}/capture.json"
        with open(capture_file, "w") as f:
            f.write(json.dumps(data))
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        resp = requests.post(
            f"{streaming_service}/api/capture",
            json={"capture_file": capture_file},
            headers=headers,
        )

        return resp

    @staticmethod
    def generate_thumbnail(video_file, output_path):
        streaming_service = get_service("falcoeye-streaming")
        output_dir = os.path.dirname(output_path)
        mkdir(output_dir)
        data = {
            "type": "thumbnail",
            "video_file": video_file,
            "output_path": output_path,
            "output_dir": output_dir,
            "capture_type": "thumbnail",
        }
        capture_file = f"{output_dir}/capture.json"
        logging.info(f"Saving capture thumbnail file in {capture_file}")
        with open(capture_file, "w") as f:
            f.write(json.dumps(data))

        headers = {"accept": "application/json", "Content-Type": "application/json"}
        resp = requests.post(
            f"{streaming_service}/api/capture",
            json={"capture_file": capture_file},
            headers=headers,
        )

        return resp
