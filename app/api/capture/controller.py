import json

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields

from app.utils import internal_err_resp, message

from .service import CaptureService

api = Namespace("capture", description="Capture related operations.")


@api.route("")
class Capture(Resource):
    @api.doc(
        "Capture media",
        # TODO: Check the other errors
        responses={200: ("Capture request succeeded")},
        security="apikey",
    )
    @jwt_required()
    def post(self):
        """Initiate a caputre request"""
        data = request.get_json()
        user_id = get_jwt_identity()
        return CaptureService.capture(user_id, data)


@api.route("/status/<registry_key>")
@api.param("registry_key", "Registry key received from capture request")
class Status(Resource):
    @api.doc(
        "Get a user media",
        responses={
            200: ("Capture status sent"),
            403: ("Access to this capture status is forbidden"),
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, registry_key):
        """Initiate a caputre status request"""
        current_user_id = get_jwt_identity()
        return CaptureService.get_capture_request_status(current_user_id, registry_key)

    # @jwt_required()
    def post(self, registry_key):
        # server_id = get_jwt_identity()
        server_id = "test"
        data = request.get_json()
        print("DATA")
        return CaptureService.set_capture_request_status(server_id, registry_key, data)
