import json

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource

from app.utils import internal_err_resp

from .dto import MediaDto
from .service import StudioService

api = MediaDto.api
vid_resp = MediaDto.video_resp
img_resp = MediaDto.image_resp


@api.route("/")
class StudioGetAllMedia(Resource):
    @api.doc(
        "Get a user media",
        responses={
            200: ("User media successfully sent"),
            404: "User not found!",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """Get a specific user's media by their username"""
        current_user_id = get_jwt_identity()
        return StudioService.get_media(current_user_id)


@api.route("/image/<string:media_id>")
class StudioImageGet(Resource):
    @api.doc(
        "Get a user media",
        responses={
            200: ("Image successfully retrieved", img_resp),
            404: "User not found!",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, media_id):
        """Get a specific user's image by their username"""
        current_user_id = get_jwt_identity()
        return StudioService.get_image(current_user_id, media_id)


@api.route("/image")
class StudioImagePost(Resource):
    required_fields = [("temprary_id", str), ("camera", int)]
    optional_fields = [("note", str, None), ("tags", str, None), ("workflow", int, -1)]

    @jwt_required()
    def post(self):
        """Add a user's image"""
        data = json.loads(request.data.decode("utf-8"))
        parsed_data = {}
        for field, ftype in StudioImagePost.required_fields:
            if field not in data:
                return internal_err_resp()
            parsed_data[field] = ftype(data[field])

        for field, ftype, fdefault in StudioImagePost.optional_fields:
            if field not in data:
                parsed_data[field] = fdefault
            else:
                parsed_data[field] = ftype(data[field])

        current_user_id = get_jwt_identity()
        parsed_data["user_id"] = current_user_id
        return StudioService.add_image(**parsed_data)

    @jwt_required()
    def delete(self):
        """Delete a specific user's image by its image_id"""
        data = json.loads(request.data.decode("utf-8"))
        if "image_id" not in data:
            return internal_err_resp()
        image_id = data["image_id"]
        current_user_id = get_jwt_identity()
        return StudioService.delete_image(current_user_id, image_id)
