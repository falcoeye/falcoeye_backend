import logging
import os
import re
from io import BytesIO

from flask import current_app, redirect, request, send_file, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource

from app.dbmodels.schemas import ImageSchema, VideoSchema
from app.utils import generate_download_signed_url_v4

from .dto import MediaDto
from .service import StudioService

logger = logging.getLogger(__name__)

api = MediaDto.api
video_resp = MediaDto.video_resp
image_resp = MediaDto.image_resp
video_post = MediaDto.video_post
image_post = MediaDto.image_post
media_resp = MediaDto.media_resp
media_count_resp = MediaDto.media_count_resp

image_schema = ImageSchema()
video_schema = VideoSchema()


@api.route("/")
class StudioList(Resource):
    @api.doc(
        "Get user's media",
        responses={200: ("media data sent", media_resp)},
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """Get user's media"""
        current_user_id = get_jwt_identity()
        orderby = request.args.get("orderby", "created_at")
        per_page = int(request.args.get("per_page", 10))
        page = int(request.args.get("page", 1))
        order_dir = request.args.get("order_dir", "asc")
        return StudioService.get_user_media(
            current_user_id, orderby, per_page, page, order_dir
        )


@api.route("/count")
class StudioListCount(Resource):
    @api.doc(
        "Get user's media count",
        responses={200: ("media count data sent", media_count_resp)},
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """Get user's media"""
        current_user_id = get_jwt_identity()
        return StudioService.get_user_media_count(current_user_id)


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

    @api.doc(
        "Edit user's image",
        responses={
            200: ("image edited", image_resp),
            404: "image not found",
        },
        security="apikey",
    )
    @jwt_required()
    def put(self, media_id):
        """Edit user's image"""
        current_user_id = get_jwt_identity()
        image_data = request.get_json()
        return StudioService.edit_image(current_user_id, media_id, image_data)


@api.route("/image/<string:media_id>/img_<string:img_size>.<extension>")
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


@api.route("/image/<string:media_id>/img_<int:img_size>.<extension>")
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

    @api.doc(
        "Edit user's video",
        responses={
            200: ("video edited", video_resp),
            404: "video not found",
        },
        security="apikey",
    )
    @jwt_required()
    def put(self, media_id):
        """Edit user's video"""
        current_user_id = get_jwt_identity()
        video_data = request.get_json()
        return StudioService.edit_video(current_user_id, media_id, video_data)


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
        logging.info(
            f'Serving video from current deployment {current_app.config["DEPLOYMENT"]}'
        )
        if (
            current_app.config["DEPLOYMENT"] == "local"
            or current_app.config["DEPLOYMENT"] == "k8s"
        ):
            url = f"{request.url_root}api/media/video/{media_id}/{current_user_id}/serve/video_{resolution}.mp4"
            return url

        video_path = f'{current_app.config["USER_ASSETS"]}/{current_user_id}/videos/{media_id}/video_{resolution}.mp4'

        # just in case
        video_path = video_path.replace("//", "/")
        bucket = current_app.config["FS_BUCKET"]
        blob_path = video_path.replace(bucket, "")
        logging.info(f"generating 15 minutes signed url for {bucket} {blob_path}")

        url = generate_download_signed_url_v4(bucket, blob_path, 15)
        logging.info(f"generated link: {url}")

        return url


@api.route(
    "/video/<string:media_id>/<string:user_id>/serve/video_<string:resolution>.mp4"
)
@api.param("media_id", "Video ID")
@api.param("user_id", "User ID")
@api.param("resolution", "Video Resolution")
class StudioVideoServeLocal(Resource):
    @api.doc(
        "Get user's video",
        security="apikey",
    )
    @jwt_required(optional=True)
    def get(self, media_id, user_id, resolution):
        """Get user's video"""

        video_path = f'{current_app.config["USER_ASSETS"]}/{user_id}/videos/{media_id}/video_{resolution}.mp4'
        logging.info(f"serving {video_path}")
        headers = request.headers

        if "range" not in headers:
            return current_app.response_class(status=400)

        size = os.stat(video_path)
        size = size.st_size
        logging.info(f"File size {size}")
        chunk_size = 10**3
        start = int(re.sub(r"\D", "", headers["range"]))
        end = min(start + chunk_size, size - 1)

        content_lenght = end - start + 1
        logging.info(f"Content Length {content_lenght}")

        def get_chunk(video_path, start, end):
            with open(video_path, "rb") as f:
                f.seek(start)
                chunk = f.read(end)
            return chunk

        headers = {
            "Content-Range": f"bytes {start}-{end}/{size}",
            "Accept-Ranges": "bytes",
            "Content-Length": content_lenght,
            "Content-Type": "video/mp4",
        }

        return current_app.response_class(
            get_chunk(video_path, start, end), 206, headers
        )


@api.route("/video/<string:media_id>/video_<int:img_size>.jpg")
@api.param("media_id", "Video ID")
@api.param("img_size", "Image Resolution")
class StudioVideoThumbnailServe(Resource):
    @api.doc(
        "Get user's video's thumbnail",
        security="apikey",
    )
    @jwt_required()
    def get(self, media_id, img_size):
        """Get user's video thumbnail"""

        current_user_id = get_jwt_identity()
        video_dir = (
            f'{current_app.config["USER_ASSETS"]}/{current_user_id}/videos/{media_id}/'
        )

        with current_app.config["FS_OBJ"].open(
            os.path.relpath(os.path.join(video_dir, f"video_{img_size}.jpg"))
        ) as f:
            img = f.read()

        return send_file(BytesIO(img), mimetype="image/jpg")
