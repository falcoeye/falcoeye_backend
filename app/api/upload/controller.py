import json
import logging

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields

from app.utils import err_resp, internal_err_resp, message

from .dto import UploadDto
from .service import UploadService

api = UploadDto.api

UPLOAD_FOLDER = "/path/to/the/uploads"
ALLOWED_EXTENSIONS = {"mp4", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@api.route("")
class Upload(Resource):
    @api.doc(
        "Upload media",
        # TODO: Check the other errors
        responses={
            200: ("upload request succeeded", UploadDto.upload_registry_key),
            417: ("something went wrong with capturing service"),
            400: ("missing file"),
            403: ("bad file"),
        },
        security="apikey",
    )
    @jwt_required()
    def post(self):
        """Initiate a caputre request"""
        user_id = get_jwt_identity()
        if "file" not in request.files:
            return err_resp(
                "missing file",
                "file_400",
                400,
            )

        file = request.files["file"]
        if not file or file.filename == "":
            return err_resp(
                "missing file",
                "file_400",
                400,
            )
        elif not allowed_file(file.filename):
            return err_resp(
                "missing file",
                "file_403",
                403,
            )
        else:
            extension = file.filename.rsplit(".", 1)[1].lower()
            if extension == "jpg" or extension == "jpeg":
                return UploadService.upload_image(user_id, file)
            elif extension == "mp4":
                return UploadService.upload_video(user_id, file)
