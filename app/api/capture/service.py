import base64
from datetime import datetime

from falcoeye_core.io import source
from flask import current_app
from PIL import Image

from app import db
from app.dbmodels.camera import Camera as Camera
from app.utils import err_resp, internal_err_resp, message

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
            # streamProvider = camera.streamProvider
            streamProvider = "youtube"
            url = "https://www.youtube.com/watch?v=tk-qJJbdOh4"

            image = source.capture_image(url, streamProvider)
            if image is None:
                resp = message(False, "Couldn't capture image. No stream found")
                return resp

            user_image_data = (
                f'{current_app.config["TEMPRARY_DATA_PATH"]}/{user_id}/images'
            )

            mkdir(user_image_data)

            temprary_id = 1
            Image.fromarray(image).save(f"{user_image_data}/{temprary_id}.jpg")

            resp = message(True, "Image has been captured.")
            resp["temprary_id"] = temprary_id
            # order='c' to skip ndarray is not C-contiguous error
            resp["image"] = base64.b64encode(image.copy(order="c")).decode("utf-8")

            return resp, 200
        except Exception as error:
            raise
            current_app.logger.error(error)
            return internal_err_resp()
