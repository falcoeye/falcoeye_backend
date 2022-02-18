import json

import requests


class Streamer:
    Host = "http://127.0.0.1:5000/"

    @staticmethod
    def capture_image(registry_key, url, stream_provider, resolution, output_path):
        data = {
            "registry_key": registry_key,
            "url": url,
            "stream_provider": stream_provider,
            "resolution": resolution,
            "output_path": output_path,
        }
        rv = requests.post(f"{Streamer.Host}/api/capture", data=json.dumps(data))

        return rv, 200

    @staticmethod
    def record_video(
        registry_key, url, stream_provider, resolution, start, end, length, output_path
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
        rv = requests.post(f"{Streamer.Host}/api/record", data=json.dumps(data))
        return rv
