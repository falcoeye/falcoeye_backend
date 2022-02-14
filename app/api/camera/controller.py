from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource

from app.dbmodels.schemas import CameraManufacturerSchema, CameraSchema
from app.utils import validation_error

from .dto import CameraDto, CameraManufacturerDto
from .service import CameraManufacturerService, CameraService

api_camera = CameraDto.api
api_manufacturer = CameraManufacturerDto.api
camera_resp = CameraDto.camera_resp
manufacturer_resp = CameraManufacturerDto.manufacturer_resp

camera_schema = CameraSchema()
manufacturer_schema = CameraManufacturerSchema()


@api_camera.route("/")
class CameraList(Resource):
    @api_camera.doc(
        "Get a list of user's cameras",
        response={
            200: ("Camera data successfully sent", camera_resp),
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
        response={
            201: ("Successfully added camera", camera_resp),
            400: "Malformed data or validations failed.",
        },
        security="apikey",
    )
    @api_camera.expect(CameraDto.camera, validate=False)
    @jwt_required()
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
        response={
            200: ("Camera data successfully sent", camera_resp),
            404: "No cameras found!",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, camera_id):
        """Show a camera item"""
        current_user_id = get_jwt_identity()
        return CameraService.get_camera_by_id(current_user_id, camera_id)

    @jwt_required()
    def delete(self, camera_id):
        """Delete a camera item"""
        current_user_id = get_jwt_identity()
        return CameraService.delete_camera(current_user_id, camera_id)

    @jwt_required()
    def put(self, camera_id):
        """Update a camera item"""
        # TODO: add service to update camera item


@api_manufacturer.route("/")
class CameraManufacturerList(Resource):
    @api_manufacturer.doc(
        "Get a list of camera manufacturer",
        response={
            200: ("Camera manufacturer data successfully sent", manufacturer_resp),
            404: "No manufacturers found!",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """Get a list of camera manufacturers"""
        return CameraManufacturerService.get_manufacturer()

    @api_manufacturer.doc(
        "Add a new camera manufacturer",
        response={
            201: ("Successfully added manufacturer", camera_resp),
            400: "Malformed data or validations failed.",
        },
        security="apikey",
    )
    @api_manufacturer.expect(CameraManufacturerDto.camera_manufacturer, validate=False)
    @jwt_required()
    def post(self):
        manufacturer_data = request.get_json()
        if errors := camera_schema.validate(manufacturer_data):
            return validation_error(False, errors), 400

        return CameraManufacturerService.create_manufacturer(data=manufacturer_data)


@api_manufacturer.route("/<manufacturer_id>")
@api_manufacturer.param("manufacturer_id", "Camera Manufacturer ID")
class Manufacturer(Resource):
    @api_manufacturer.doc(
        "Show a camera manufacturer item",
        response={
            200: ("Manufacturer data successfully sent", camera_resp),
            404: "No manufacturers found!",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, manufacturer_id):
        """Show a manufacturer item"""
        return CameraManufacturerService.get_manufacturer_by_id(manufacturer_id)

    @jwt_required()
    def delete(self, manufacturer_id):
        """Delete a manufacturer item"""
        current_user_id = get_jwt_identity()
        return CameraManufacturerService.delete_manufacturer(
            current_user_id, manufacturer_id
        )

    @jwt_required()
    def put(self, manufacturer_id):
        """Update a manufacturer item"""
        # TODO: add service to update manufacturer item
