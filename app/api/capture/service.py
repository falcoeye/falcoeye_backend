import logging

from flask import current_app, request

from app import db
from app.api.registry import change_status, register
from app.dbmodels.camera import Camera as Camera
from app.dbmodels.registry import Registry
from app.dbmodels.user import Permission, User
from app.utils import (
    err_resp,
    exists,
    generate_download_signed_url_v4,
    internal_err_resp,
    message,
    mkdir,
    rmtree,
)

from .streamer import Streamer
from .utils import load_registry_data

logger = logging.getLogger(__name__)


class CaptureService:
    @staticmethod
    def capture(user_id, data):
        """Capture media"""
        camera_id = data.get("camera_id", None)
        capture_type = data.get("capture_type", None)
        logger.info(f"Capture request {camera_id} {capture_type} from {user_id}")

        if not camera_id or not capture_type:
            return err_resp(
                "missing camera id or capture type",
                "media_400",
                400,
            )

        if capture_type == "image":
            return CaptureService.capture_image(user_id, camera_id)
        elif capture_type == "video":
            length = data.get("length", 60)
            return CaptureService.record_video(user_id, camera_id, length=length)

    @staticmethod
    def get_all_registry_keys(admin_id):

        if not (user := User.query.filter_by(id=admin_id).first()):
            return err_resp("user not found", "user_400", 400)

        logger.info(f"Is {user.id} admin?")
        logger.info(f"{user.has_permission(Permission.CHANGE_CAPTURE_STATUS)}")
        # only admin is allowed
        if not user.has_permission(Permission.CHANGE_CAPTURE_STATUS):
            return err_resp("unauthorized", "role_401", 401)

        logging.info("Retrieving all registry items")
        if not (registry_keys := Registry.query.all()):
            return err_resp("no registry found", "registry_404", 404)

        try:
            registry_data = load_registry_data(registry_keys, many=True)
            resp = message(True, "analysis data sent")
            resp["registry"] = registry_data
            return resp, 200
        except Exception as error:
            logger.error(error)
            return internal_err_resp()

    @staticmethod
    def has_camera_capture(user_id):
        # There should be one of this
        reg_key = Registry.query.filter(
            Registry.status.in_(("SUCCEEDED", "STARTED")), Registry.user == user_id
        ).first()
        return reg_key is not None

    @staticmethod
    def capture_image(user_id, camera_id):

        if not (
            camera := Camera.query.filter_by(owner_id=user_id, id=camera_id).first()
        ):
            return err_resp("camera not found", "camera_404", 404)

        # TODO: find another response number
        if CaptureService.has_camera_capture(user_id):
            return err_resp(
                "something went wrong with capturing service", "capture_417", 417
            )

        try:
            # preparing storing information
            logger.info(f"Capture image request {camera_id} from {user_id}")
            user_image_data = (
                f'{current_app.config["TEMPORARY_DATA_PATH"]}/{user_id}/images/'
            )

            # creating a new registry item
            registry_object = register(user_id, camera_id, "image", user_image_data)
            logger.info(f"Registry created {str(registry_object.id)}")
            # Create capturing request
            resp = Streamer.capture_image(
                str(registry_object.id), camera, registry_object.capture_path
            )
            logger.info(f"Response from streaming received {resp.status_code}")

            if resp.status_code == 200:
                resp = message(True, "capture request succeeded")
                resp["registry_key"] = str(registry_object.id)
                # resp["temporary_path"] = registry_object.capture_path
                return resp, 200
            else:
                # setting registry status to capturing
                change_status(str(registry_object.id), "FAILED")
                response = err_resp(
                    "something went wrong with capturing service",
                    "capture_417",
                    417,
                )
                return response, 417

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def record_video(user_id, camera_id, length=60):
        if not (
            camera := Camera.query.filter_by(owner_id=user_id, id=camera_id).first()
        ):
            return err_resp("camera not found", "camera_404", 404)

        # TODO: find another response number
        if CaptureService.has_camera_capture(user_id):
            return err_resp(
                "something went wrong with capturing service", "capture_417", 417
            )

        try:

            # preparing storing information
            user_video_data = (
                f'{current_app.config["TEMPORARY_DATA_PATH"]}/{user_id}/videos/'
            )
            mkdir(user_video_data)

            # creating a new registry key
            registry_object = register(user_id, camera_id, "video", user_video_data)

            # Create recording request. Output path (registry_object.capture_path)
            # is created in register function
            resp = Streamer.record_video(
                str(registry_object.id), camera, length, registry_object.capture_path
            )
            logger.info(f"Response from streaming received {resp.status_code}")
            if resp.status_code == 200:
                resp = message(True, "capture request succeeded")
                resp["registry_key"] = str(registry_object.id)
                resp["temporary_path"] = registry_object.capture_path
                return resp, 200
            else:
                # setting registry status to capturing
                change_status(str(registry_object.id), "FAILED")
                response = err_resp(
                    "something went wrong with capturing service",
                    "capture_404",
                    404,
                )
                return response, 404

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_capture_data(user_id, registry_key):
        if not (registry_item := Registry.query.filter_by(id=registry_key).first()):
            # TODO: check on the numbers 403, and 404
            return err_resp("registry key not found", "not_found_403", 403)

        resp = message(True, "capture data sent")

        resp["capture_status"] = registry_item.status
        resp["registry_key"] = registry_key
        if registry_item.status == "SUCCEEDED":
            bucket = current_app.config["FS_BUCKET"]
            blob_path = registry_item.capture_path.replace(bucket, "")
            logging.info(f"generating 15 minutes signed url for {bucket} {blob_path}")

            if (
                current_app.config["DEPLOYMENT"] == "local"
                or current_app.config["DEPLOYMENT"] == "k8s"
            ):
                if registry_item.media_type == "video":
                    resp[
                        "temporary_path"
                    ] = f"{request.url_root}api/capture/video/{user_id}/videos/{registry_key}.mp4"
                elif registry_item.media_type == "image":
                    resp[
                        "temporary_path"
                    ] = f"{request.url_root}api/capture/image/{user_id}/images/{registry_key}.jpg"
            else:
                resp["temporary_path"] = generate_download_signed_url_v4(
                    bucket, blob_path, 15
                )
            logging.info(f'generated link: {resp["temporary_path"]}')
        else:
            resp["temporary_path"] = None

        return resp, 200

    @staticmethod
    def set_capture_data(admin_id, registry_key, data):

        new_status = data.get("capture_status")
        logger.info(
            f"Received registery status change request for {registry_key} from {admin_id}: {new_status}"
        )
        if not (user := User.query.filter_by(id=admin_id).first()):
            return err_resp("user not found", "user_400", 400)

        logger.info(f"Is {user.id} admin?")
        logger.info(f"{user.has_permission(Permission.CHANGE_CAPTURE_STATUS)}")
        # only admin is allowed
        if not user.has_permission(Permission.CHANGE_CAPTURE_STATUS):
            return err_resp("unauthorized", "role_401", 401)

        status = change_status(registry_key, new_status)
        if not status:
            return err_resp("request failed", "role_417", 417)

        return message(True, "capture data changed"), 200

    @staticmethod
    def _delete_capture(capture_obj):

        db.session.delete(capture_obj)
        db.session.commit()
        if capture_obj.media_type == "image":
            capture_data = f'{current_app.config["TEMPORARY_DATA_PATH"]}/{capture_obj.user}/images/{capture_obj.id}'
        elif capture_obj.media_type == "video":
            capture_data = f'{current_app.config["TEMPORARY_DATA_PATH"]}/{capture_obj.user}/videos/{capture_obj.id}'

        if exists(capture_data):
            rmtree(capture_data)

        resp = message(True, "analysis deleted")
        return resp, 200

    @staticmethod
    def delete_capture(user_id, capture_id):
        """Delete a capture from DB by id and user id"""
        if not (user := User.query.filter_by(id=user_id).first()):
            return err_resp("user not found", "user_400", 400)
        logging.info(f"deleting capture {capture_id} by {user_id}")
        if user.has_permission(Permission.CHANGE_CAPTURE_STATUS):
            if not (capture_req := Registry.query.filter_by(id=capture_id).first()):
                return err_resp(
                    "capture not found",
                    "capture_404",
                    404,
                )
        elif not (
            capture_req := Registry.query.filter_by(user=user_id, id=capture_id).first()
        ):
            return err_resp(
                "capture not found",
                "analysis_404",
                404,
            )
        if not capture_req:
            logging.info(f"unauthorized call {capture_req}")
            return err_resp("unauthorized", "role_401", 401)

        try:
            return CaptureService._delete_capture(capture_req)
        except Exception as error:
            logger.error(error)
            return internal_err_resp()
