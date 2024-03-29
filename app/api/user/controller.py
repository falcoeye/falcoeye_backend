from flask import current_app, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource

from .dto import UserDto
from .service import UserService

api = UserDto.api
data_resp = UserDto.data_resp


@api.route("/profile")
class UserGet(Resource):
    @api.doc(
        "Get a specific user",
        responses={
            200: ("user data sent", data_resp),
            404: "user not found",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """Get a specific user's data by their username"""
        current_user_id = get_jwt_identity()
        return UserService.get_user_data(current_user_id)


@api.route("/edit")
class UserEdit(Resource):
    @api.doc(
        "Edit a specific user",
        responses={
            200: ("user data sent", data_resp),
            403: "username or email exists",
            404: "user not found",
        },
        security="apikey",
    )
    @jwt_required()
    def put(self):
        """Edit a specific user's data by their username"""
        current_user_id = get_jwt_identity()
        user_data = request.get_json()
        return UserService.edit_user(current_user_id, user_data)
