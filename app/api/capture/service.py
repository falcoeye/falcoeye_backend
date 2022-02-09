import base64
from datetime import datetime

from falcoeye_core.io import source
from flask import current_app

from app import db
from app.dbmodels.camera import Camera as Camera
from app.utils import err_resp, internal_err_resp, message


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
            streamProvider = "angelcam"
            url = "https://v.angelcam.com/iframe?v=16lb6045r4"

            image = source.capture_image(url, streamProvider)
            if image is None:
                resp = message(False, "Couldn't capture image. No stream found")
                return resp

            temprary_id = 1
            resp = message(True, "Image has been captured.")
            resp["temprary_id"] = temprary_id
            resp["image"] = base64.b64encode(image)
            return resp, 200
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
