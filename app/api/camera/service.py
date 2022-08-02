import base64
import os
from datetime import datetime

from flask import current_app

from app import db
from app.dbmodels.camera import Camera
from app.dbmodels.schemas import CameraSchema
from app.utils import err_resp, internal_err_resp, message, mkdir, put

from .utils import load_camera_data

basedir = os.path.abspath(os.path.dirname(__file__))

camera_schema = CameraSchema()


class CameraService:
    @staticmethod
    def get_user_cameras(user_id):
        """Get a list of cameras"""
        if not (cameras := Camera.query.filter_by(owner_id=user_id).all()):
            return err_resp("no camera found", "camera_404", 404)

        try:
            camera_data = load_camera_data(cameras, many=True)
            resp = message(True, "camera data sent")
            resp["camera"] = camera_data

            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_camera_by_id(user_id, camera_id):
        """Get camera by ID"""
        if not (
            camera := Camera.query.filter_by(owner_id=user_id, id=camera_id).first()
        ):
            return err_resp("camera not found", "camera_404", 404)

        try:
            camera_data = load_camera_data(camera)
            resp = message(True, "camera data sent")
            resp["camera"] = camera_data

            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def delete_camera(user_id, camera_id):
        """Delete camera from DB by camera ID"""
        if not (
            camera := Camera.query.filter_by(owner_id=user_id, id=camera_id).first()
        ):
            return err_resp("camera not found", "camera_404", 404)

        try:
            db.session.delete(camera)
            db.session.commit()

            resp = message(True, "camera deleted")
            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def create_camera(user_id, data):

        # check if manufacturer exists

        name = data["name"]
        streaming_type = data["streaming_type"]
        host = data.get("host", None)
        port = data.get("port", None)
        username = data.get("username", None)
        password = data.get("password", None)
        url = data.get("url", None)
        latitude = data.get("latitude", None)
        longitude = data.get("longitude", None)
        status = data.get("status", "stopped")
        created_at = datetime.utcnow()
        image = data.get("image", None)

        # check if camera exists
        if Camera.query.filter_by(owner_id=user_id, name=name).first():
            return err_resp("camera already exists", "existing_camera", 403)

        try:
            new_camera = Camera(
                name=name,
                url=url,
                host=host,
                port=port,
                username=username,
                password=password,
                owner_id=user_id,
                streaming_type=streaming_type,
                latitude=latitude,
                longitude=longitude,
                status=status,
                created_at=created_at,
            )

            db.session.add(new_camera)
            db.session.flush()

            camera_dir = (
                f'{current_app.config["USER_ASSETS"]}/{user_id}/cameras/{new_camera.id}'
            )

            mkdir(camera_dir)

            base64_img = data.get("image", None)
            camera_img = f"{camera_dir}/img_original.jpg"
            if base64_img:
                imgdata = base64.b64decode(base64_img)
                with open(camera_img, "wb") as f:
                    f.write(imgdata)
            else:
                put(f"{basedir}/assets/default_camera_img.jpg", camera_img)

            camera_info = camera_schema.dump(new_camera)
            db.session.commit()

            resp = message(True, "camera added")
            resp["camera"] = camera_info

            return resp, 201

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def update_camera_by_id(user_id, camera_id, data):

        if not (
            camera := Camera.query.filter_by(owner_id=user_id, id=camera_id).first()
        ):
            return err_resp("camera not found", "camera_404", 404)

        name = data.get("name", camera.name)
        streaming_type = data.get("streaming_type", camera.streaming_type)
        url = data.get("url", camera.url)
        host = data.get("host", camera.host)
        port = data.get("port", camera.port)
        username = data.get("username", camera.username)
        password = data.get("password", camera.password)
        latitude = data.get("latitude", camera.latitude)
        longitude = data.get("longitude", camera.longitude)
        status = data.get("status", camera.status)

        try:
            camera.name = name
            camera.url = url
            camera.host = host
            camera.port = port
            camera.username = username
            camera.password = password
            camera.owner_id = user_id
            camera.streaming_type = streaming_type
            camera.latitude = latitude
            camera.longitude = longitude
            camera.status = status

            db.session.flush()
            db.session.commit()
            camera_data = load_camera_data(camera)

            resp = message(True, "camera edited")
            resp["camera"] = camera_data

            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
