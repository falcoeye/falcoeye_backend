import base64
import os
import shutil
from datetime import datetime

import dateutil.parser
from flask import current_app

from app import db
from app.dbmodels.camera import Camera  # , CameraManufacturer
from app.dbmodels.schemas import CameraSchema  # , CameraManufacturerSchema
from app.utils import err_resp, internal_err_resp, message

from .utils import load_camera_data, mkdir

basedir = os.path.abspath(os.path.dirname(__file__))

camera_schema = CameraSchema()
# manufacturer_schema = CameraManufacturerSchema()


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
        # manufacturer_id = data["manufacturer_id"]
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

        # check if manufacturer exists
        """if not (
            manufacturer := CameraManufacturer.query.filter_by(
                id=manufacturer_id
            ).first()
        ):
            return err_resp(
                "Manufacturer is not registered", "invalid_manufacturer", 403
            )"""

        try:
            new_camera = Camera(
                name=name,
                url=url,
                host=host,
                port=port,
                username=username,
                password=password,
                owner_id=user_id,
                # manufacturer_id=manufacturer.id,
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
                shutil.copy2(f"{basedir}/assets/default_camera_img.jpg", camera_img)

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
        # manufacturer_id = data.get("manufacturer_id", camera.manufacturer_id)
        streaming_type = data.get("streaming_type", camera.streaming_type)
        url = data.get("url", camera.url)
        host = data.get("host", camera.host)
        port = data.get("port", camera.port)
        username = data.get("username", camera.username)
        password = data.get("password", camera.password)
        latitude = data.get("latitude", camera.latitude)
        longitude = data.get("longitude", camera.longitude)
        status = data.get("status", camera.status)
        created_at = camera.created_at

        # check if manufacturer exists
        # if not (
        #     manufacturer := CameraManufacturer.query.filter_by(
        #         id=manufacturer_id
        #     ).first()
        # ):
        #     return err_resp(
        #         "Manufacturer is not registered", "invalid_manufacturer", 403
        #     )

        try:
            updated_camera = Camera(
                name=name,
                url=url,
                host=host,
                port=port,
                username=username,
                password=password,
                owner_id=user_id,
                # manufacturer_id=manufacturer_id,
                streaming_type=streaming_type,
                latitude=latitude,
                longitude=longitude,
                status=status,
                created_at=created_at,
            )
            camera = updated_camera
            db.session.commit()

            resp = message(True, "camera edited")

            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()


"""class CameraManufacturerService:
    @staticmethod
    def get_manufacturer():
        """ """Get a list of camera manufacturer""" """
        if not (manufacturers := CameraManufacturer.query.all()):
            return err_resp("No manufacturer founds!", "manufacturer_404", 404)

        try:
            manufacturer_data = load_manufacturer_data(manufacturers, many=True)
            resp = message(True, "Manufacturer data sent")
            resp["manufacturer"] = manufacturer_data

            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_manufacturer_by_id(manufacturer_id):
        """ """Get camera manufacturer by ID""" """
        if not (
            manufacturer := CameraManufacturer.query.filter_by(
                id=manufacturer_id
            ).first()
        ):
            return err_resp("Manufacturer not found!", "manufacturer_404", 404)

        try:
            manufacturer_data = load_manufacturer_data(manufacturer)
            resp = message(True, "Manufacturer data sent")
            resp["manufacturer"] = manufacturer_data

            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_manufacturer_by_name(manufacturer_name):
        """ """Get camera manufacturer by name""" """
        if not (
            manufacturer := CameraManufacturer.query.filter_by(
                name=manufacturer_name
            ).first()
        ):
            return err_resp("Manufacturer not found!", "manufacturer_404", 404)

        try:
            manufacturer_data = load_manufacturer_data(manufacturer)
            resp = message(True, "Manufacturer data sent")
            resp["manufacturer"] = manufacturer_data

            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def create_manufacturer(data):
        name = data["name"]

        # check if manufacturer exists
        if CameraManufacturer.query.filter_by(name=name).first():
            return err_resp("Manufacturer already exist", "existing_manufacturer", 403)

        try:
            new_manufacturer = CameraManufacturer(
                name=name,
            )

            db.session.add(new_manufacturer)
            db.session.flush()

            manufacturer_info = manufacturer_schema.dump(new_manufacturer)
            db.session.commit()

            resp = message(True, "Successfully added manufacturer")
            resp["manufacturer"] = manufacturer_info

            return resp, 201

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def delete_manufacturer(user_id, manufacturer_id):
        """ """Delete manufacturer from DB by manufacturer ID""" """

        # TODO: check if user is admin before deleting manufacturer

        if not (
            manufacturer := CameraManufacturer.query.filter_by(
                id=manufacturer_id
            ).first()
        ):
            return err_resp("Manufacturer not found!", "manufacturer_404", 404)

        try:
            db.session.delete(manufacturer)
            db.session.commit()

            resp = message(True, "Manufacturer deleted")
            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()"""
