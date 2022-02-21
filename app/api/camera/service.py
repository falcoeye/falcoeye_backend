import dateutil.parser
from flask import current_app

from app import db
from app.dbmodels.camera import Camera, CameraManufacturer, Streamer
from app.dbmodels.schemas import CameraManufacturerSchema, CameraSchema, StreamerSchema
from app.utils import err_resp, internal_err_resp, message

from .utils import load_camera_data, load_manufacturer_data, load_streamer_data

camera_schema = CameraSchema()
manufacturer_schema = CameraManufacturerSchema()
streamer_schema = StreamerSchema()


class CameraService:
    @staticmethod
    def get_user_cameras(user_id):
        """Get a list of cameras"""
        if not (cameras := Camera.query.filter_by(owner_id=user_id).all()):
            return err_resp("No camera founds!", "camera_404", 404)

        try:
            camera_data = load_camera_data(cameras, many=True)
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
        manufacturer_id = data["manufacturer_id"]
        streamer_id = data["streamer_id"]
        url = data["url"]

        utm_x = data.get("utm_x")
        utm_y = data.get("utm_y")
        resolution_x = data.get("resolution_x")
        resolution_y = data.get("resolution_y")
        status = data.get("status")
        connection_date = data.get("connection_date")
        if connection_date:
            connection_date = dateutil.parser.isoparse(connection_date)

        # check if manufacturer exists
        if not (
            manufacturer := CameraManufacturer.query.filter_by(
                id=manufacturer_id
            ).first()
        ):
            return err_resp(
                "Manufacturer is not registered", "invalid_manufacturer", 403
            )

        if not (streamer := Streamer.query.filter_by(id=streamer_id).first()):
            return err_resp("streamer is not registered", "invalid_streamer", 403)

        try:
            new_camera = Camera(
                name=name,
                url=url,
                owner_id=user_id,
                manufacturer_id=manufacturer.id,
                streamer_id=streamer.id,
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

            resp = message(True, "Camera has been added")
            resp["camera"] = camera_info

            return resp, 201

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()


class CameraManufacturerService:
    @staticmethod
    def get_manufacturer():
        """Get a list of camera manufacturer"""
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
        """Get camera manufacturer by ID"""
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
        """Get camera manufacturer by name"""
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
            return err_resp("Manufacturer does exist", "existing_manufacturer", 403)

        try:
            new_manufacturer = CameraManufacturer(
                name=name,
            )

            db.session.add(new_manufacturer)
            db.session.flush()

            manufacturer_info = manufacturer_schema.dump(new_manufacturer)
            db.session.commit()

            resp = message(True, "Manufacturer has been added")
            resp["manufacturer"] = manufacturer_info

            return resp, 201

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def delete_manufacturer(user_id, manufacturer_id):
        """Delete manufacturer from DB by manufacturer ID"""

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
            return internal_err_resp()


class StreamerService:
    @staticmethod
    def get_streamer():
        """Get a list of camera streamer"""
        if not (streamers := Streamer.query.all()):
            return err_resp("No streamer founds!", "streamer_404", 404)

        try:
            streamer_data = load_streamer_data(streamers, many=True)
            resp = message(True, "Streamer data sent")
            resp["streamer"] = streamer_data

            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_streamer_by_id(streamer_id):
        """Get camera streamer by ID"""
        if not (streamer := Streamer.query.filter_by(id=streamer_id).first()):
            return err_resp("Streamer not found!", "streamer_404", 404)

        try:
            streamer_data = load_streamer_data(streamer)
            resp = message(True, "Streamer data sent")
            resp["streamer"] = streamer_data

            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_streamer_by_name(streamer_name):
        """Get camera streamer by name"""
        if not (streamer := Streamer.query.filter_by(name=streamer_name).first()):
            return err_resp("Streamer not found!", "streamer_404", 404)

        try:
            streamer_data = load_streamer_data(streamer)
            resp = message(True, "Streamer data sent")
            resp["streamer"] = streamer_data

            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def create_streamer(data):
        name = data["name"]

        # check if streamer exists
        if Streamer.query.filter_by(name=name).first():
            return err_resp("Streamer does exist", "existing_streamer", 403)

        try:
            new_streamer = Streamer(
                name=name,
            )

            db.session.add(new_streamer)
            db.session.flush()

            streamer_info = streamer_schema.dump(new_streamer)
            db.session.commit()

            resp = message(True, "Streamer has been added")
            resp["streamer"] = streamer_info

            return resp, 201

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def delete_streamer(user_id, streamer_id):
        """Delete streamer from DB by streamer ID"""

        # TODO: check if user is admin before deleting streamer

        if not (streamer := Streamer.query.filter_by(id=streamer_id).first()):
            return err_resp("Streamer not found!", "streamer_404", 404)

        try:
            db.session.delete(streamer)
            db.session.commit()

            resp = message(True, "Streamer deleted")
            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
