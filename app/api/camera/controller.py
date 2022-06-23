from flask import current_app, request, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource

from app.dbmodels.schemas import CameraSchema  # , CameraManufacturerSchema
from app.utils import validation_error

from .dto import CameraDto  # , CameraManufacturerDto
from .service import CameraService  # ,CameraManufacturerService

api_camera = CameraDto.api
# api_manufacturer = CameraManufacturerDto.api


camera_schema = CameraSchema()
# manufacturer_schema = CameraManufacturerSchema()


@api_camera.route("/")
class CameraList(Resource):
    @api_camera.doc(
        "Get a list of user's cameras",
        responses={
            200: ("Camera data successfully sent", CameraDto.camera_list),
            404: "No cameras found!",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """Get a list of user's cameras"""
        current_user_id = get_jwt_identity()
        return CameraService.get_user_cameras(current_user_id)

    @api_camera.doc(
        "Add a new camera",
        responses={
            201: ("Successfully added camera", CameraDto.camera_resp),
            403: ("Camera already exists or Manufacturer is not registered"),
            400: "Malformed data or validations failed.",
        },
        security="apikey",
    )
    @jwt_required()
    @api_camera.expect(CameraDto.camera_post, validate=False)
    def post(self):
        camera_data = request.get_json()
        user_id = get_jwt_identity()
        if errors := camera_schema.validate(camera_data):
            return validation_error(False, errors), 400

        return CameraService.create_camera(user_id=user_id, data=camera_data)


@api_camera.route("/<camera_id>")
@api_camera.param("camera_id", "Camera ID")
class Camera(Resource):
    @api_camera.doc(
        "Show a camera item",
        responses={
            200: ("Camera data successfully sent", CameraDto.camera_resp),
            404: "No cameras found!",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, camera_id):
        """Show a camera item"""
        current_user_id = get_jwt_identity()
        return CameraService.get_camera_by_id(current_user_id, camera_id)

    @api_camera.doc(
        "Delete a user camera",
        responses={
            200: ("Camera successfully deleted"),
            404: "Camera not found!",
        },
        security="apikey",
    )
    @jwt_required()
    def delete(self, camera_id):
        """Delete a camera item"""
        current_user_id = get_jwt_identity()
        return CameraService.delete_camera(current_user_id, camera_id)

    @api_camera.doc(
        "Edit a user camera",
        responses={
            200: ("Camera successfully edited", CameraDto.camera_resp),
            404: "Camera not found!",
        },
        security="apikey",
    )
    @api_camera.expect(CameraDto.camera_post, validate=False)
    @jwt_required()
    def put(self, camera_id):
        """Update a camera item"""
        camera_data = request.get_json()
        current_user_id = get_jwt_identity()
        return CameraService.update_camera_by_id(
            current_user_id, camera_id, camera_data
        )


@api_camera.route("/<camera_id>/img_<img_size>")
@api_camera.param("camera_id", "Camera ID")
@api_camera.param("img_size", "Image Size")
class Camera(Resource):
    @api_camera.doc(
        "Show a camera item",
        responses={
            200: ("Camera data successfully sent", CameraDto.camera_resp),
            404: "No cameras found!",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, camera_id, img_size):
        """Show a camera item"""
        user_id = get_jwt_identity()
        return send_from_directory(
            f'{current_app.config["USER_ASSETS"]}/{user_id}/{camera_id}',
            f"img_{img_size}.jpg",
            mimetype="image/jpg",
        )


"""@api_manufacturer.route("/")
class CameraManufacturerList(Resource):
    @api_manufacturer.doc(
        "Get a list of camera manufacturer",
        responses={
            200: (
                "Camera manufacturer data successfully sent",
                CameraManufacturerDto.manufacturer_list,
            ),
            404: "No manufacturers found!",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """ """Get a list of camera manufacturers""" """
        return CameraManufacturerService.get_manufacturer()

    @api_manufacturer.doc(
        "Add a new camera manufacturer",
        responses={
            201: (
                "Successfully added manufacturer",
                CameraManufacturerDto.manufacturer_resp,
            ),
            403: "Manufacturer already exist",
            400: "Malformed data or validations failed.",
        },
        security="apikey",
    )
    @jwt_required()
    @api_manufacturer.expect(
        CameraManufacturerDto.camera_manufacturer_post, validate=False
    )
    def post(self):
        manufacturer_data = request.get_json()
        if errors := manufacturer_schema.validate(manufacturer_data):
            return validation_error(False, errors), 400

        return CameraManufacturerService.create_manufacturer(data=manufacturer_data)


@api_manufacturer.route("/<manufacturer_id>")
@api_manufacturer.param("manufacturer_id", "Camera Manufacturer ID")
class CameraManufacturer(Resource):
    @api_manufacturer.doc(
        "Show a camera manufacturer item",
        responses={
            200: (
                "Manufacturer data successfully sent",
                CameraManufacturerDto.manufacturer_resp,
            ),
            404: "No manufacturers found!",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, manufacturer_id):
        """ """Show a manufacturer item""" """
        return CameraManufacturerService.get_manufacturer_by_id(manufacturer_id)

    @jwt_required()
    def delete(self, manufacturer_id):
        """ """Delete a manufacturer item""" """
        current_user_id = get_jwt_identity()
        return CameraManufacturerService.delete_manufacturer(
            current_user_id, manufacturer_id
        )

    @api_camera.doc(
        "Edit a camera maniufacturer",
        responses={
            200: (
                "Maniufacturer successfully edited",
                CameraManufacturerDto.manufacturer_resp,
            ),
            404: "Maniufacturer not found!",
        },
        security="apikey",
    )
    @api_camera.expect(CameraManufacturerDto.camera_manufacturer_post, validate=False)
    @jwt_required()
    def put(self, manufacturer_id):
        """ """Update a manufacturer item""" """
        # TODO: add service to update manufacturer item
        pass"""
