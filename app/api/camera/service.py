import base64
import io
import logging
import os
from datetime import datetime

from flask import current_app
from PIL import Image
from sqlalchemy import desc

from app import db
from app.dbmodels.camera import Camera
from app.dbmodels.registry import Registry
from app.dbmodels.schemas import CameraSchema
from app.utils import (
    err_resp,
    generate_download_signed_url_v4,
    internal_err_resp,
    message,
    mkdir,
    put,
)

from .utils import load_camera_data

basedir = os.path.abspath(os.path.dirname(__file__))

camera_schema = CameraSchema()
orderby_dict = {
    "name": Camera.name,
    "streaming_type": Camera.streaming_type,
    "created_at": Camera.created_at,
    "status": Camera.status,
    "name_desc": desc(Camera.name),
    "streaming_type_desc": desc(Camera.streaming_type),
    "created_at_desc": desc(Camera.created_at),
    "status_desc": desc(Camera.status),
}


class CameraService:
    @staticmethod
    def get_user_cameras(user_id, orderby, per_page, page, order_dir):
        """Get a list of cameras"""
        if order_dir == "desc":
            orderby += "_desc"
        orderby = orderby_dict.get(orderby, Camera.name)
        query = (
            Camera.query.filter_by(owner_id=user_id)
            .order_by(orderby)
            .paginate(page, per_page=per_page)
        )
        if not (cameras := query.items):
            return err_resp("no camera found", "camera_404", 404)
        lastPage = not query.has_next
        registry = CameraService.get_registry(user_id)

        try:
            camera_data = load_camera_data(cameras, many=True)
            resp = message(True, "camera data sent")
            resp["camera"] = camera_data
            resp["registry"] = registry
            resp["lastPage"] = lastPage
            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_user_camera_count(user_id):
        """Get user data by username"""
        camera_count = Camera.query.filter_by(owner_id=user_id).count()
        try:
            resp = message(True, "camera count data sent")
            resp["camera_count"] = camera_count
            return resp, 200
        except Exception as error:
            logging.error(error)
            return internal_err_resp()

    @staticmethod
    def get_registry(user_id, camera_id=None):
        # There should be one of this
        reg_key = Registry.query.filter(
            Registry.status.in_(("SUCCEEDED", "STARTED")),
            Registry.user == user_id
            # Registry.camera_id == camera_id,
        ).first()

        registry = {}
        if reg_key:
            registry["capture_status"] = reg_key.status
            registry["registry_key"] = str(reg_key.id)
            if reg_key.status == "SUCCEEDED":
                bucket = current_app.config["FS_BUCKET"]
                blob_path = reg_key.capture_path.replace(bucket, "")
                logging.info(
                    f"generating 15 minutes signed url for {bucket} {blob_path}"
                )
                registry["temporary_path"] = generate_download_signed_url_v4(
                    bucket, blob_path, 15
                )
                logging.info(f'generated link: {registry["temporary_path"]}')
            else:
                registry["temporary_path"] = None

        return registry

    @staticmethod
    def get_camera_by_id(user_id, camera_id):
        """Get camera by ID"""
        if not (
            camera := Camera.query.filter_by(owner_id=user_id, id=camera_id).first()
        ):
            return err_resp("camera not found", "camera_404", 404)

        registry = CameraService.get_registry(user_id, camera_id)

        try:
            camera_data = load_camera_data(camera)
            resp = message(True, "camera data sent")
            resp["camera"] = camera_data
            resp["registry"] = registry
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
        status = data.get("status", "running")
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
            thumbnail_img = f"{camera_dir}/img_260.jpg"
            if base64_img:
                imgdata = base64.b64decode(base64_img)
                with current_app.config["FS_OBJ"].open(
                    os.path.relpath(camera_img), "wb"
                ) as f:
                    f.write(imgdata)

                logging.info("Adding camera thumbnail")
                buffer = io.BytesIO()
                img = Image.open(io.BytesIO(imgdata))
                img.thumbnail((260, 260))
                img.save(buffer, format="JPEG")
                with current_app.config["FS_OBJ"].open(
                    os.path.relpath(thumbnail_img), "wb"
                ) as f:
                    f.write(buffer.getbuffer())
            else:
                logging.info("No camera image. Copying default")
                put(f"{basedir}/assets/default_camera_img.jpg", camera_img)
                put(f"{basedir}/assets/default_camera_img_260.jpg", thumbnail_img)

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
