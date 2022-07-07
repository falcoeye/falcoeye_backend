import logging

from flask import current_app

from app import db
from app.api.registry import change_status, register
from app.dbmodels.registry import Registry
from app.utils import err_resp, internal_err_resp, message

from .utils import mkdir


class UploadService:
    @staticmethod
    def upload_image(user_id, img_file):

        # preparing storing information
        logging.info(f"Upload image request from {user_id}")
        user_image_data = (
            f'{current_app.config["TEMPORARY_DATA_PATH"]}/{user_id}/images'
        )
        mkdir(user_image_data)
        # creating a new registry item
        registry_object = register(user_id, None, "image", user_image_data)
        logging.info(f"Registry created {str(registry_object.id)}")
        # Create capturing request
        try:
            img_file.save(registry_object.capture_path)
            resp = message(True, "upload request succeeded")
            resp["registry_key"] = str(registry_object.id)
            change_status(str(registry_object.id), "SUCCEEDED")
            return resp, 200
        except Exception as error:
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
        logging.info(f"Upload video request from {user_id}")
        user_video_data = (
            f'{current_app.config["TEMPORARY_DATA_PATH"]}/{user_id}/videos'
        )
        mkdir(user_video_data)
        # creating a new registry item
        registry_object = register(user_id, None, "video", user_video_data)
        logging.info(f"Registry created {str(registry_object.id)}")
        # Create capturing request
        try:
            video_file.save(registry_object.capture_path)
            resp = message(True, "upload request succeeded")
            resp["registry_key"] = str(registry_object.id)
            change_status(str(registry_object.id), "SUCCEEDED")
            return resp, 200
        except Exception as error:
            # setting registry status to capturing
            change_status(str(registry_object.id), "FAILED")
            err_resp(
                "something went wrong with capturing service",
                "upload_417",
                417,
            )
            return err_resp, 417
