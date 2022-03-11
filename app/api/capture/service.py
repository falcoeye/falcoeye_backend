from flask import current_app

from app.dbmodels.camera import Camera as Camera
from app.dbmodels.camera import Streamer as DBStreamer
from app.utils import err_resp, internal_err_resp, message

from .registry import Registry
from .streamer import Streamer
from .utils import mkdir


class CaptureService:
    @staticmethod
    def capture(user_id, data):
        """Capture media"""
        camera_id = data.get("camera_id", None)
        capture_type = data.get("capture_type", None)
        if not camera_id:
            return err_resp("No camera provided", "media_400", 400)
        if not capture_type:
            return err_resp("No capture type provided", "media_400", 400)

        if capture_type == "image":
            return CaptureService.capture_image(user_id, camera_id)
        elif capture_type == "video":
            start = data.get("start", -1)
            end = data.get("end", -1)
            length = data.get("length", -1)
            return CaptureService.record_video(
                user_id, camera_id, start=start, end=end, length=length
            )

    @staticmethod
    def capture_image(user_id, camera_id):
        if not (
            camera := Camera.query.filter_by(owner_id=user_id, id=camera_id).first()
        ):
            return err_resp("Camera not found!", "camera_404", 404)

        try:
            # accessing camera information
            url = camera.url
            streamer_id = camera.streamer_id
            streamer = DBStreamer.query.filter_by(id=streamer_id).first()
            resolution = "1080px"  # camera.resolution

            # creating a new registry key
            registry_key = Registry.create_key(user_id, camera_id)

            # preparing storing information
            user_image_data = (
                f'{current_app.config["TEMPORARY_DATA_PATH"]}/{user_id}/images'
            )
            mkdir(user_image_data)
            output_path = f"{user_image_data}/{registry_key}.jpg"

            # setting registry status to capturing
            Registry.register_capturing(registry_key)

            # Create capturing request
            resp, status_code = Streamer.capture_image(
                registry_key, url, streamer.name, resolution, output_path
            )
            if status_code == 200:
                resp = message(True, "Capture image request successfully submitted")
                resp["registry_key"] = registry_key
                return resp, 200
            else:
                # setting registry status to capturing
                Registry.register_failed_to_capture(registry_key)
                return resp, status_code

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_capture_request_status(user_id, registry_key):

        capture_user = registry_key.split("_")[0]
        # checking if allowed
        if str(user_id) != capture_user:
            return err_resp(
                "Access to this capture status is forbidden", "capture_status_403", 403
            )

        status = Registry.check_status(registry_key)
        resp = message(True, "Capture status sent")
        if not status:
            resp["capture_status"] = "unknown"
        else:
            resp["capture_status"] = status
        return resp, 200

    @staticmethod
    def set_capture_request_status(server_id, registry_key, data):
        # role = Role.query.filter_by(
        #     id=User.query.filter_by(user_id=server_id).first().role_id
        # ).first()
        # if not role.has_permission(16):
        #     return err_resp(
        #         "Access to this capture status is forbidden", "capture_status_403", 403
        #     )

        new_status = data.get("capture_status")
        Registry.set_capture_request_status(registry_key, new_status)
        CaptureService.what_after(registry_key, new_status)

        return message(True, "Change status has been handled"), 200

    @staticmethod
    def what_after(registry_key, capture_status):
        if capture_status == "CAPTURED" or capture_status == "RECORDED":
            Registry.register_ready_to_submit(registry_key)
        elif capture_status == "FAILEDTOCAPTURE":
            pass

    @staticmethod
    def record_video(user_id, camera_id, start, end, length):
        if not (
            camera := Camera.query.filter_by(owner_id=user_id, id=camera_id).first()
        ):
            return err_resp("Camera not found!", "camera_404", 404)

        try:
            # accessing camera information
            url = camera.url
            streamer_id = camera.streamer_id
            streamer = DBStreamer.query.filter_by(id=streamer_id).first()
            resolution = "1080p"  # camera.resolution

            # creating a new registry key
            registry_key = Registry.create_key(user_id, camera_id)

            # preparing storing information
            user_video_data = (
                f'{current_app.config["TEMPORARY_DATA_PATH"]}/{user_id}/videos'
            )
            mkdir(user_video_data)
            output_path = f"{user_video_data}/{registry_key}.mp4"

            # setting registry status to recording
            Registry.register_recording(registry_key)

            # Create recording request
            resp, status_code = Streamer.record_video(
                registry_key,
                url,
                streamer.name,
                resolution,
                start,
                end,
                length,
                output_path,
            )
            print(resp, status_code)

            if status_code == 200:
                resp = message(True, "Capture image request successfully submitted")
                resp["registry_key"] = registry_key
                return resp, 200
            else:
                # setting registry status to capturing
                Registry.register_failed_to_capture(registry_key)
                return resp, status_code

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
