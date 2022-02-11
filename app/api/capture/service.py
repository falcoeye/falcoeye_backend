import base64
from datetime import datetime

from falcoeye_core.io import source
from flask import current_app
from PIL import Image

from app import db
from app.dbmodels.camera import Camera as Camera
from app.utils import err_resp, internal_err_resp, message

from .registry import Registry
from .streamer import Streamer
from .utils import mkdir


class CaptureService:
    @staticmethod
    def capture(user_id, camera_id, capture_type, start=-1, end=-1, length=-1):
        """Capture media"""
        if capture_type == "image":
            return CaptureService.capture_image(user_id, camera_id)

    @staticmethod
    def capture_image(user_id, camera_id):
        try:
            # camera = Camera.query.filter_by(owner=user_id, id=camera_id).first()
            # for now
            # camera = Camera()
            # url = camera.url
            # stream_provider = camera.streamProvider

            key = Registry.create_key(user_id, camera_id)
            stream_provider = "youtube"
            url = "https://www.youtube.com/watch?v=tk-qJJbdOh4"

            user_image_data = (
                f'{current_app.config["TEMPRARY_DATA_PATH"]}/{user_id}/images'
            )
            mkdir(user_image_data)
            output_path = f"{user_image_data}/{key}.jpg"

            resp = Streamer.capture_image(
                key, url, stream_provider, "1080p", output_path
            )
            if resp.status_code != 200:
                # TOKNOW: 2
                return internal_err_resp()

            Registry.register_capture(key)

            resp = message(True, "Capture image request been submitted.")
            resp["registry_key"] = key

            return resp, 200
        except Exception as error:
            raise
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_capture_request_status(key):
        status = Registry.check_status(key)
        resp = message(True, "Status message")
        if not status:
            resp["status"] = "unknown"
        else:
            resp["status"] = status
        return resp, 200

    @staticmethod
    def capture_video(user_id, camera_id, start, end, length):

        # camera = Camera.query.filter_by(owner=user_id, id=camera_id).first()
        # for now
        # camera = Camera()
        # url = camera.url
        # streamProvider = camera.streamProvider
        streamProvider = "angelcam"
        url = "https://v.angelcam.com/iframe?v=16lb6045r4"

        key = Registry.register_record(user_id, camera_id)
        if not key:
            return internal_err_resp()

        resp = message(True, "Recording has started.")
        resp["registry_key"] = key

        return resp, 200
