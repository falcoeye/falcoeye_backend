from flask import request
from flask_restx import Resource

from app.utils import validation_error

from .dto import AuthDto
from .service import AuthService
from .utils import LoginSchema, RegisterSchema

# Auth modules

api = AuthDto.api
auth_success = AuthDto.auth_success

login_schema = LoginSchema()
register_schema = RegisterSchema()


@api.route("/login")
class AuthLogin(Resource):
    """User login endpoint
    User registers then receives the user's information and access_token
    """

    auth_login = AuthDto.auth_login

    @api.doc(
        "Auth login",
        responses={
            200: ("successfully logged in", auth_success),
            400: "validations failed",
            401: "incorrect username or password",
            404: "email not found",
        },
    )
    @api.expect(auth_login, validate=False)
    def post(self):
        """Login using email and password"""
        # Grab the json data
        login_data = request.get_json()
        # Validate data
        if errors := login_schema.validate(login_data):
            return validation_error(False, errors), 400

        return AuthService.login(login_data)


@api.route("/register")
class AuthRegister(Resource):
    """User register endpoint
    User registers then receives the user's information and access_token
    """

    auth_register = AuthDto.auth_register

    @api.doc(
        "Auth registration",
        responses={
            201: ("successfully registered", auth_success),
            400: "malformed data or validations failed",
            403: "email or username already exists",
        },
    )
    @api.expect(auth_register, validate=False)
    def post(self):
        """User registration"""
        # Grab the json data
        register_data = request.get_json()
        # Validate data
        if errors := register_schema.validate(register_data):
            return validation_error(False, errors), 400

        return AuthService.register(register_data)
