from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource

from app.dbmodels.schemas import CameraManufacturerSchema, CameraSchema
from app.utils import validation_error

from .dto import CameraDto
from .service import CameraService

api = CameraDto.api
camera_resp = CameraDto.camera_resp
manufacturer_resp = CameraDto.manufacturer_resp

camera_schema = CameraSchema()
manufacturer_schema = CameraManufacturerSchema()


@api.route("/")
class Camera(Resource):
    @api.doc(
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

    @api.doc(
        "Add a new camera",
        response={
            201: ("Successfully added camera", camera_resp),
            400: "Malformed data or validations failed.",
        },
        security="apikey",
    )
    @api.expect(CameraDto.camera, validate=True)
    @jwt_required()
    def post(self):
        camera_data = request.get_json()
        user_id = get_jwt_identity()
        if errors := camera_schema.validate(camera_data):
            return validation_error(False, errors), 400

        return CameraService.create_camera(user_id=user_id, data=camera_data)
