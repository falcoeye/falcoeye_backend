from flask import current_app

from app import db
from app.api.registry import change_status, get_status, register
from app.dbmodels.camera import Camera as Camera
from app.dbmodels.registry import Registry
from app.dbmodels.user import Permission, Role, User
from app.utils import err_resp, internal_err_resp, message

from .streamer import Streamer
from .utils import mkdir


class CaptureService:
    @staticmethod
    def capture(user_id, data):
        """Capture media"""
        camera_id = data.get("camera_id", None)
        capture_type = data.get("capture_type", None)

        if not camera_id or not capture_type:
            return err_resp(
                "Missing data: Camera id and capture type must be provided",
                "media_400",
                400,
            )

        if capture_type == "image":
            return CaptureService.capture_image(user_id, camera_id)
        elif capture_type == "video":
            length = data.get("length", 60)
            return CaptureService.record_video(user_id, camera_id, length=length)

    @staticmethod
    def capture_image(user_id, camera_id):

        if not (
            camera := Camera.query.filter_by(owner_id=user_id, id=camera_id).first()
        ):
            return err_resp("Camera not found!", "camera_404", 404)

        try:
            # preparing storing information
            user_image_data = (
                f'{current_app.config["TEMPORARY_DATA_PATH"]}/{user_id}/images'
            )
            mkdir(user_image_data)

            # creating a new registry item
            registry_object = register(user_id, camera_id, "image", user_image_data)

            # Create capturing request
            resp = Streamer.capture_image(
                str(registry_object.id), camera, registry_object.capture_path
            )

            if resp.status_code == 200:
                resp = message(True, "Capture request succeeded")
                resp["registry_key"] = str(registry_object.id)
                return resp, 200
            else:
                # setting registry status to capturing
                change_status(str(registry_object.id), "FAILED")
                err_resp(
                    "Something went wrong. Couldn't initialize capturing request",
                    "capture_403",
                    403,
                )
                return err_resp, 403

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def record_video(user_id, camera_id, length=60):
        if not (
            camera := Camera.query.filter_by(owner_id=user_id, id=camera_id).first()
        ):
            return err_resp("Camera not found!", "camera_404", 404)

        try:

            # preparing storing information
            user_video_data = (
                f'{current_app.config["TEMPORARY_DATA_PATH"]}/{user_id}/videos'
            )
            mkdir(user_video_data)

            # creating a new registry key
            registry_object = register(user_id, camera_id, "video", user_video_data)

            # Create recording request. Output path (registry_object.capture_path)
            # is created in register function
            resp = Streamer.record_video(
                str(registry_object.id), camera, length, registry_object.capture_path
            )

            if resp.status_code == 200:
                resp = message(True, "Capture request succeeded")
                resp["registry_key"] = str(registry_object.id)
                return resp, 200
            else:
                # setting registry status to capturing
                change_status(str(registry_object.id), "FAILED")
                err_resp(
                    "Something went wrong. Couldn't initialize capturing request",
                    "capture_404",
                    404,
                )
                return err_resp, 404

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_capture_data(user_id, registry_key, data):
        if not (registry_item := Registry.query.filter_by(id=registry_key).first()):
            # TODO: check on the numbers 403, and 404
            return err_resp("Registry key not found", "not_found_403", 403)

        if registry_item.status == "STARTED":
            return err_resp("Capture data is not ready", "not_ready_400", 400)

        resp = message(True, "Capture status sent")
        resp["capture_path"] = registry_item.capture_path

        return resp, 200

    @staticmethod
    def get_capture_status(user_id, registry_key):

        if not (registry_status := get_status(registry_key)):
            # TODO: check on the numbers 403
            return err_resp("Registry key not found", "not_found_403", 403)

        resp = message(True, "Capture status sent")
        resp["capture_status"] = registry_status
        return resp, 200

    @staticmethod
    def set_capture_status(server_id, registry_key, data):
        if not (user := User.query.filter_by(id=server_id).first()):
            return err_resp("User not found!", "user_404", 404)

        # only admin is allowed
        if not user.has_permission(Permission.CHANGE_CAPTURE_STATUS):
            return err_resp("Access denied", "role_403", 403)

        new_status = data.get("status")
        change_status(registry_key, new_status)
        return message(True, "Change status has been handled"), 200
