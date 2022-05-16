import json

import requests

from app.utils import internal_err_resp, message


class Streamer:
    @staticmethod
    def capture_image(
        registry_key, url, stream_provider, resolution, output_path, streamer_host
    ):
        data = {
            "registry_key": registry_key,
            "url": url,
            "stream_provider": stream_provider,
            "resolution": resolution,
            "output_path": output_path,
        }
        # TODO: re-implement streamer microservices with ducker and k8s in mind
        # rv = requests.post(f"{streamer_host}/api/capture", data=json.dumps(data))
        resp = message(True, "Capture request initiated")
        return resp, 200

    @staticmethod
    def record_video(
        registry_key,
        url,
        stream_provider,
        resolution,
        start,
        end,
        length,
        output_path,
        streamer_host,
    ):

        # handle scheduling here
        if end > 0:
            length = min(60, end - start)
        elif length <= 0:
            length = 60

        data = {
            "registry_key": registry_key,
            "url": url,
            "stream_provider": stream_provider,
            "resolution": resolution,
            "length": length,
            "output_path": output_path,
        }
        # TODO: re-implement streamer microservices with ducker and k8s in mind
        # rv = requests.post(f"{streamer_host}/api/record", data=json.dumps(data))
        resp = message(True, "Record request initiated")
        return resp, 200
