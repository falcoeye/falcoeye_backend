import json
import logging

from flask import request
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
            200: ("Capture request succeeded", CaptureDto.capture_registry_key),
            400: ("Missing data: Camera id and capture type must be provided"),
            403: ("Something went wrong. Couldn't initialize capturing request"),
            404: ("Camera not found!"),
        },
        security="apikey",
    )
    @jwt_required()
    @api.expect(CaptureDto.capture_post_data, validate=False)
    def post(self):
        """Initiate a caputre request"""
        data = request.get_json()
        user_id = get_jwt_identity()
        return CaptureService.capture(user_id, data)


@api.route("/<registry_key>")
@api.param("registry_key", "Registry key received from capture request")
class CaptureData(Resource):
    @api.doc(
        "Get a user capture data path",
        responses={
            200: ("Capture data sent", CaptureDto.capture_data),
            403: ("Registry key not found"),
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, registry_key):
        """Get a user capture data path"""
        current_user_id = get_jwt_identity()
        return CaptureService.get_capture_data(current_user_id, registry_key)

    @api.doc(
        "Post a user capture data status",
        responses={
            200: ("Change capture data been handled"),
            400: ("Capture data is not ready"),
            403: ("Registry key not found"),
        },
        security="apikey",
    )
    @jwt_required()
    def post(self, registry_key):
        admin_id = get_jwt_identity()
        data = request.get_json()
        logging.info(f"Received new data for {registry_key} by {admin_id}")
        return CaptureService.set_capture_data(admin_id, registry_key, data)
