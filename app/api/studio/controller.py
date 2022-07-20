import logging
import os
from io import BytesIO

from flask import current_app, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource

from app.dbmodels.schemas import ImageSchema, VideoSchema

from .dto import MediaDto
from .service import StudioService

logger = logging.getLogger(__name__)

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
        "Get user's media",
        responses={
            200: ("media data sent", media_resp),
            204: "no media found",
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
            200: ("image data sent", image_resp),
            404: "image not found",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, media_id):
        """Get user's image data"""
        current_user_id = get_jwt_identity()
        return StudioService.get_image(current_user_id, media_id)

    @api.doc(
        "Delete user's image data",
        responses={
            200: ("image deleted"),
            404: "image not found",
            204: "content not found",
            417: "deletion partially failed",
        },
        security="apikey",
    )
    @jwt_required()
    def delete(self, media_id):
        """Delete user's image"""
        current_user_id = get_jwt_identity()
        return StudioService.delete_image(current_user_id, media_id)


@api.route("/image/<string:media_id>/video_<string:img_size>.<extension>")
@api.param("media_id", "Image ID")
@api.param("img_size", "Image Resolution")
@api.param("extension", "Image Extension")
class StudioImageServe(Resource):
    @api.doc(
        "Get user's image",
        responses={},
        security="apikey",
    )
    @jwt_required()
    def get(self, media_id, img_size, extension):
        """Get user's image"""
        current_user_id = get_jwt_identity()
        image_dir = (
            f'{current_app.config["USER_ASSETS"]}/{current_user_id}/images/{media_id}/'
        )

        with current_app.config["FS_OBJ"].open(
            os.path.relpath(os.path.join(image_dir, f"img_{img_size}.{extension}"))
        ) as f:
            img = f.read()

        return send_file(BytesIO(img), mimetype="image/jpg")


@api.route("/image")
class StudioImagePost(Resource):
    @api.doc(
        "Post a user image",
        responses={
            200: ("image added", MediaDto.image),
            403: "invalid registry key",
            417: "process failed",
        },
        security="apikey",
    )
    @api.expect(MediaDto.image_post, validate=False)
    @jwt_required()
    def post(self):
        """Add a user's image"""
        image_data = request.get_json()
        user_id = get_jwt_identity()
        logger.info(f"Received new image from {user_id} with data {image_data}")
        return StudioService.create_image(user_id=user_id, data=image_data)


@api.route("/video/<string:media_id>")
@api.param("media_id", "Video ID")
class StudioVideoGet(Resource):
    @api.doc(
        "Get user's video data",
        responses={
            200: ("video data sent", video_resp),
            404: "video not found",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, media_id):
        """Get user's video data"""
        current_user_id = get_jwt_identity()
        return StudioService.get_video(current_user_id, media_id)

    @api.doc(
        "Delete user's video",
        responses={
            200: ("video deleted"),
            404: "video not found",
            204: "content not found",
            417: "deletion partially failed",
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
        "Post user's video",
        responses={
            200: ("video added", MediaDto.video),
            403: "invalid registry key",
            417: "process failed",
        },
        security="apikey",
    )
    @api.expect(MediaDto.video_post, validate=False)
    @jwt_required()
    def post(self):
        """Add user's video"""
        video_data = request.get_json()
        user_id = get_jwt_identity()
        return StudioService.create_video(user_id=user_id, data=video_data)


@api.route("/video/<string:media_id>/video_<string:resolution>.mp4")
@api.param("media_id", "Video ID")
@api.param("resolution", "Video Resolution")
class StudioVideoServe(Resource):
    @api.doc(
        "Get user's video",
        security="apikey",
    )
    @jwt_required()
    def get(self, media_id, resolution):
        """Get user's video"""
        current_user_id = get_jwt_identity()
        video_path = f'{current_app.config["USER_ASSETS"]}/{current_user_id}/videos/{media_id}/video_{resolution}.mp4'

        # size = os.stat(video_path)
        # size = size.st_size
        # chunk_size = 10**3
        # start = int(re.sub("\D", "", headers["range"]))
        # end = min(start + chunk_size, size - 1)

        # content_lenght = end - start + 1

        # def get_chunk(video_path, start, end):
        #     with open(video_path, "rb") as f:
        #         f.seek(start)
        #         chunk = f.read(end)
        #     return chunk

        # headers = {
        #     "Content-Range": f"bytes {start}-{end}/{size}",
        #     "Accept-Ranges": "bytes",
        #     "Content-Length": content_lenght,
        #     "Content-Type": "video/mp4",
        # }

        # return current_app.response_class(
        #     get_chunk(video_path, start, end), 206, headers
        # )
        return None
