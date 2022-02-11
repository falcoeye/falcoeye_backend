import json

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields

from app.utils import internal_err_resp

from .service import CaptureService

api = Namespace("capture", description="Capture related operations.")


@api.route("")
class Capture(Resource):
    required_fields = [("capture_type", str), ("camera_id", int)]
    optional_fields = [("start", int, None), ("end", int, None), ("length", int, -1)]

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
        print(data)
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
    required_fields = [("key", str)]

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

        current_user_id = get_jwt_identity()
        # checking if allowed
        if current_user_id != parsed_data["key"].split("_")[0]:
            return internal_err_resp()

        return CaptureService.get_capture_request_status(**parsed_data)
