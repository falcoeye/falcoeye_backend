import logging
import os

from flask import current_app

from app.api.registry import change_status, register
from app.utils import err_resp, message, mkdir

logger = logging.getLogger(__name__)


class UploadService:
    @staticmethod
    def upload_image(user_id, img_file):

        # preparing storing information
        logger.info(f"Upload image request from {user_id}")
        user_image_data = (
            f'{current_app.config["TEMPORARY_DATA_PATH"]}/{user_id}/images/'
        )
        mkdir(user_image_data)
        # creating a new registry item
        registry_object = register(user_id, None, "image", user_image_data)
        logger.info(f"Registry created {str(registry_object.id)}")
        # Create capturing request
        try:
            with current_app.config["FS_OBJ"].open(
                os.path.relpath(registry_object.capture_path), "wb"
            ) as f:
                f.write(img_file.stream.read())

            resp = message(True, "upload request succeeded")
            resp["registry_key"] = str(registry_object.id)
            change_status(str(registry_object.id), "SUCCEEDED")
            return resp, 200
        except Exception as error:
            logger.error(error)
            # setting registry status to capturing
            change_status(str(registry_object.id), "FAILED")
            err_resp(
                "something went wrong with capturing service",
                "upload_417",
                417,
            )
            return err_resp, 417

    @staticmethod
    def upload_video(user_id, video_file):
        # preparing storing information
        logger.info(f"Upload video request from {user_id}")
        user_video_data = (
            f'{current_app.config["TEMPORARY_DATA_PATH"]}/{user_id}/videos/'
        )
        mkdir(user_video_data)
        # creating a new registry item
        registry_object = register(user_id, None, "video", user_video_data)
        logger.info(f"Registry created {str(registry_object.id)}")
        # Create capturing request
        try:
            with current_app.config["FS_OBJ"].open(
                os.path.relpath(registry_object.capture_path), "wb"
            ) as f:
                f.write(video_file.stream.read())

            resp = message(True, "upload request succeeded")
            resp["registry_key"] = str(registry_object.id)
            change_status(str(registry_object.id), "SUCCEEDED")
            return resp, 200
        except Exception as error:
            logger.error(error)
            # setting registry status to capturing
            change_status(str(registry_object.id), "FAILED")
            err_resp(
                "something went wrong with capturing service",
                "upload_417",
                417,
            )
            return err_resp, 417
