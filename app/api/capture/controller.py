import json

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields

from app.utils import internal_err_resp, message

from .service import CaptureService

api = Namespace("capture", description="Capture related operations.")


@api.route("")
class Capture(Resource):
    required_fields = [("capture_type", str), ("camera_id", int)]
    optional_fields = [("start", int, -1), ("end", int, -1), ("length", int, -1)]

    @api.doc(
        "Get a user media",
        responses={
            200: ("User media successfully sent"),
            404: "User not found!",
        },
        security="apikey",
    )
    @jwt_required()
    def post(self):
        """Initiate a caputre request"""
        data = json.loads(request.data.decode("utf-8"))
        parsed_data = {}

        for field, ftype in Capture.required_fields:
            if field not in data:
                return internal_err_resp()
            parsed_data[field] = ftype(data[field])

        for field, ftype, fdefault in Capture.optional_fields:
            if field not in data:
                parsed_data[field] = fdefault
            else:
                parsed_data[field] = ftype(data[field])

        current_user_id = get_jwt_identity()
        parsed_data["user_id"] = current_user_id

        return CaptureService.capture(**parsed_data)


@api.route("/status")
class Status(Resource):
    required_fields = [("registry_key", str)]

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
        """Initiate a caputre status request"""
        data = json.loads(request.data.decode("utf-8"))
        parsed_data = {}
        for field, ftype in Status.required_fields:
            if field not in data:
                return internal_err_resp()
            parsed_data[field] = ftype(data[field])

        current_user_id = get_jwt_identity()
        capture_user = int(parsed_data["registry_key"].split("_")[0])
        # checking if allowed
        if current_user_id != capture_user:
            return internal_err_resp()

        return CaptureService.get_capture_request_status(**parsed_data)

    def post(self):
        required_fields = Status.required_fields + [("capture_status", str)]
        data = json.loads(request.data.decode("utf-8"))
        parsed_data = {}
        for field, ftype in required_fields:
            if field not in data:
                return internal_err_resp()
            parsed_data[field] = ftype(data[field])
        CaptureService.set_capture_request_status(**parsed_data)
        # checking if allowed (only from other services)
        CaptureService.what_after(**parsed_data)

        return message(True, "Change status has been handled"), 200
