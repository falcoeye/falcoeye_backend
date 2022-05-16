import json

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource

from app.dbmodels.schemas import ImageSchema, VideoSchema
from app.utils import internal_err_resp, validation_error

from .dto import MediaDto
from .service import StudioService

api = MediaDto.api
video_resp = MediaDto.video_resp
image_resp = MediaDto.image_resp
video_post = MediaDto.video_post
image_post = MediaDto.image_post
media_resp = MediaDto.media_resp

image_schema = ImageSchema()
video_schema = VideoSchema()


@api.route("/")
class StudioList(Resource):
    @api.doc(
        "Get a user media",
        responses={
            200: ("User media successfully sent", media_resp),
            204: "No medias found!",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """Get user's media"""
        current_user_id = get_jwt_identity()
        return StudioService.get_user_media(current_user_id)


@api.route("/image/<media_id>")
@api.param("media_id", "Image ID")
class StudioImageGet(Resource):
    @api.doc(
        "Get a user media",
        responses={
            200: ("Image successfully sent", image_resp),
            404: "Image not found!",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, media_id):
        """Get user's image"""
        current_user_id = get_jwt_identity()
        return StudioService.get_image(current_user_id, media_id)

    @api.doc(
        "Delete a user image",
        responses={
            200: ("Image successfully deleted"),
            404: "Image not found!",
        },
        security="apikey",
    )
    @jwt_required()
    def delete(self, media_id):
        """Delete user's image"""
        current_user_id = get_jwt_identity()
        return StudioService.delete_image(current_user_id, media_id)


@api.route("/image")
class StudioImagePost(Resource):
    @api.doc(
        "Get a user media",
        responses={
            200: ("Image successfully added", MediaDto.image),
            403: "Invalid registry key",
        },
        security="apikey",
    )
    @api.expect(MediaDto.image_post, validate=False)
    @jwt_required()
    def post(self):
        """Add a user's image"""
        image_data = request.get_json()
        if errors := image_schema.validate(image_data):
            return validation_error(False, errors), 400
        user_id = get_jwt_identity()
        return StudioService.create_image(user_id=user_id, data=image_data)


@api.route("/video/<string:media_id>")
@api.param("media_id", "Video ID")
class StudioVideoGet(Resource):
    @api.doc(
        "Get user's video",
        responses={
            200: ("Video successfully sent", video_resp),
            404: "Video not found!",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, media_id):
        """Get user's video"""
        current_user_id = get_jwt_identity()
        return StudioService.get_video(current_user_id, media_id)

    @api.doc(
        "Delete user's video",
        responses={
            200: ("Video successfully deleted"),
            404: "Video not found!",
        },
        security="apikey",
    )
    @jwt_required()
    def delete(self, media_id):
        """Delete user's video"""
        current_user_id = get_jwt_identity()
        return StudioService.delete_video(current_user_id, media_id)


@api.route("/video")
class StudioVideoPost(Resource):
    @api.doc(
        "Get a user media",
        responses={
            200: ("Video successfully added", MediaDto.video),
            403: "Invalid registry key",
        },
        security="apikey",
    )
    @api.expect(MediaDto.video_post, validate=False)
    @jwt_required()
    def post(self):
        """Add a user's video"""
        video_data = request.get_json()
        if errors := video_schema.validate(video_data):
            return validation_error(False, errors), 400
        user_id = get_jwt_identity()
        return StudioService.create_video(user_id=user_id, data=video_data)
