from flask import Blueprint
from flask_restx import Api

from .user.controller import api as user_ns

authorizations = {
    "apikey": {"type": "apiKey", "in": "header", "name": "X-API-KEY"}
}

# Import controller APIs as namespaces.
api_bp = Blueprint("api", __name__)

api = Api(api_bp, title="API", description="Main routes.",authorizations=authorizations)

# API namespaces
api.add_namespace(user_ns)
