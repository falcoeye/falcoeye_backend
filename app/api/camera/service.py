from flask import current_app

from app import db
from app.dbmodels.camera import Camera, CameraManufacturer
from app.dbmodels.schemas import CameraManufacturerSchema, CameraSchema
from app.utils import err_resp, internal_err_resp, message

from .utils import load_camera_data, load_manufacturer_data

camera_schema = CameraSchema()
manufacturer_schema = CameraManufacturerSchema()


class CameraService:
    @staticmethod
    def get_user_cameras(user_id):
        """Get a list of cameras"""
        if not (cameras := Camera.query.filter_by(owner_id=user_id).all()):
            return err_resp("No camera founds!", "camera_404", 404)

        try:
            camera_data = load_camera_data(cameras)
            resp = message(True, "Camera data sent")
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
            return err_resp("Camera not found!", "camera_404", 404)

        try:
            camera_data = load_camera_data(camera)
            resp = message(True, "Camera data sent")
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
            return err_resp("Camera not found!", "camera_404", 404)

        try:
            db.session.delete(camera)
            db.session.commit()

            resp = message(True, "Camera deleted")
            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def create_camera(user_id, data):
        name = data["name"]
        manufacturer = data["manufacturer"]
        url = data["url"]

        utm_x = data.get("utm_x")
        utm_y = data.get("utm_y")
        resolution_x = data.get("resolution_x")
        resolution_y = data.get("resolution_y")
        status = data.get("status")
        connection_date = data.get("connection_date")

        # check if manufacturer exists
        if not (
            manufacturer := CameraManufacturer.filter_by(name=manufacturer).first()
        ):
            return err_resp(
                "Manufacturer is not registered", "invalid_manufacturer", 403
            )

        try:
            new_camera = Camera(
                name=name,
                owner_id=user_id,
                manufacturer_id=manufacturer.id,
                utm_x=utm_x,
                utm_y=utm_y,
                resolution_x=resolution_x,
                resolution_y=resolution_y,
                status=status,
                connection_date=connection_date,
            )

            db.session.add(new_camera)
            db.session.flush()

            camera_info = camera_schema.dump(new_camera)
            db.session.commit()

            resp = message(True, "Camera has been added.")
            resp["camera"] = camera_info

            return resp, 201

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
