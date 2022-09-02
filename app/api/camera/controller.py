import os
from io import BytesIO

from flask import current_app, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource

from app.dbmodels.schemas import CameraSchema
from app.utils import validation_error

from .dto import CameraDto
from .service import CameraService

api_camera = CameraDto.api


camera_schema = CameraSchema()


@api_camera.route("/")
class CameraList(Resource):
    @api_camera.doc(
        "Get a list of user's cameras",
        responses={
            200: ("camera data sent", CameraDto.camera_list),
            404: "no camera found",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """Get a list of user's cameras"""
        current_user_id = get_jwt_identity()
        orderby = request.args.get("orderby", "name")
        per_page = int(request.args.get("per_page", 10))
        page = int(request.args.get("page", 1))
        order_dir = request.args.get("order_dir", "asc")
        return CameraService.get_user_cameras(
            current_user_id, orderby, per_page, page, order_dir
        )

    @api_camera.doc(
        "Add a new camera",
        responses={
            201: ("camera added", CameraDto.camera_resp),
            403: "camera already exists",
            400: "malformed data or validations failed",
        },
        security="apikey",
    )
    @jwt_required()
    @api_camera.expect(CameraDto.camera_post, validate=False)
    def post(self):
        camera_data = request.get_json()
        user_id = get_jwt_identity()

        return CameraService.create_camera(user_id=user_id, data=camera_data)


@api_camera.route("/count")
class CameraListCount(Resource):
    @api_camera.doc(
        "Get user's camera count",
        responses={200: ("camera count data sent", CameraDto.camera_count_resp)},
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """Get user's camera count"""
        current_user_id = get_jwt_identity()
        return CameraService.get_user_camera_count(current_user_id)


@api_camera.route("/<camera_id>")
@api_camera.param("camera_id", "Camera ID")
class Camera(Resource):
    @api_camera.doc(
        "Get user's camera by ID",
        responses={
            200: ("camera data sent", CameraDto.camera_resp),
            404: "camera not found",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, camera_id):
        """Get user's camera by ID"""
        current_user_id = get_jwt_identity()
        return CameraService.get_camera_by_id(current_user_id, camera_id)

    @api_camera.doc(
        "Delete user's camera by ID",
        responses={
            200: "camera deleted",
            404: "camera not found",
        },
        security="apikey",
    )
    @jwt_required()
    def delete(self, camera_id):
        """Delete a camera item"""
        current_user_id = get_jwt_identity()
        return CameraService.delete_camera(current_user_id, camera_id)

    @api_camera.doc(
        "Edit user's camera",
        responses={
            200: ("camera edited", CameraDto.camera_resp),
            404: "camera not found",
        },
        security="apikey",
    )
    @api_camera.expect(CameraDto.camera_post, validate=False)
    @jwt_required()
    def put(self, camera_id):
        """Update user's camera"""
        camera_data = request.get_json()
        current_user_id = get_jwt_identity()
        return CameraService.update_camera_by_id(
            current_user_id, camera_id, camera_data
        )


@api_camera.route("/<camera_id>/img_<img_size>.jpg")
@api_camera.param("camera_id", "Camera ID")
@api_camera.param("img_size", "Image Size")
class Camera(Resource):
    @api_camera.doc(
        "Get camera's thumbnail image",
        security="apikey",
    )
    @jwt_required()
    def get(self, camera_id, img_size):
        """Get camera's thumbnail image"""
        user_id = get_jwt_identity()

        with current_app.config["FS_OBJ"].open(
            os.path.relpath(
                os.path.join(
                    f'{current_app.config["USER_ASSETS"]}/{user_id}/cameras/{camera_id}',
                    f"img_{img_size}.jpg",
                )
            )
        ) as f:
            img = f.read()

        return send_file(
            BytesIO(img),
            mimetype="image/jpg",
        )
