import json
import logging
import os
import re
from io import BytesIO

from flask import current_app, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields

from app.utils import internal_err_resp, message

from .dto import CaptureDto
from .service import CaptureService

api = CaptureDto.api


@api.route("")
class Capture(Resource):
    @api.doc(
        "Capture media",
        # TODO: Check the other errors
        responses={
            200: ("capture request succeeded", CaptureDto.capture_registry_key),
            400: ("missing camera id or capture type"),
            417: ("something went wrong with capturing service"),
            404: ("camera not found"),
        },
        security="apikey",
    )
    @jwt_required()
    @api.expect(CaptureDto.capture_post_data, validate=False)
    def post(self):
        """Initiate a caputre request"""
        data = request.get_json()
        user_id = get_jwt_identity()
        logging.info(f"Capture request with {data}")
        return CaptureService.capture(user_id, data)

    @api.doc(
        """Get a list of all registry keys""",
        responses={
            200: ("registry data sent", CaptureDto.registry_list),
            400: ("user not found"),
            404: "no registry found",
            401: ("unauthorized"),
        },
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """Get a list of all user registry"""
        user_id = get_jwt_identity()
        return CaptureService.get_all_registry_keys(user_id)


@api.route("/<registry_key>")
@api.param("registry_key", "Registry key received from capture request")
class CaptureData(Resource):
    @api.doc(
        "Get capture data",
        responses={
            200: ("capture data sent", CaptureDto.capture_data),
            403: ("registry key not found"),
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, registry_key):
        """Get a user capture data path"""
        current_user_id = get_jwt_identity()
        return CaptureService.get_capture_data(current_user_id, registry_key)

    @api.doc(
        "Set capture data",
        responses={
            200: ("capture data changed"),
            400: ("user not found"),
            417: ("request failed"),
            401: ("unauthorized"),
        },
        security="apikey",
    )
    @jwt_required()
    def put(self, registry_key):
        admin_id = get_jwt_identity()
        data = request.get_json()
        logging.info(f"Received new data for {registry_key} by {admin_id}")
        return CaptureService.set_capture_data(admin_id, registry_key, data)

    @api.doc(
        "Delete user's capture request",
        responses={
            200: ("capture deleted"),
            404: "capture not found",
            417: "deletion partially failed",
            401: ("unauthorized"),
        },
        security="apikey",
    )
    @jwt_required()
    def delete(self, registry_key):
        """Delete user's video"""
        current_user_id = get_jwt_identity()
        return CaptureService.delete_capture(current_user_id, registry_key)


@api.route("/video/<string:user_id>/videos/<string:registry_key>.mp4")
@api.param("user_id", "User ID")
@api.param("registry_key", "Registry key")
class CaptureVideoServeLocal(Resource):
    @api.doc(
        "Get user's video",
        security="apikey",
    )
    @jwt_required(optional=True)
    def get(self, user_id, registry_key):
        """Get user's video"""

        video_path = f'{current_app.config["TEMPORARY_DATA_PATH"]}/{user_id}/videos/{registry_key}.mp4'
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


@api.route("/image/<string:user_id>/images/<string:registry_key>.jpg")
@api.param("user_id", "User ID")
@api.param("registry_key", "Registry key")
class CaptureImageServeLocal(Resource):
    @api.doc(
        "Get user's video",
        security="apikey",
    )
    @jwt_required(optional=True)
    def get(self, user_id, registry_key):
        """Get user's video"""

        image_path = f'{current_app.config["TEMPORARY_DATA_PATH"]}/{user_id}/images/{registry_key}.jpg'
        logging.info(f"serving {image_path}")
        with current_app.config["FS_OBJ"].open(image_path) as f:
            img = f.read()

        return send_file(BytesIO(img), mimetype="image/jpg")
