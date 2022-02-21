from flask import Blueprint
from flask_restx import Api

from .camera.controller import api_camera as camera_ns
from .camera.controller import api_manufacturer as manufacturer_ns
from .camera.controller import api_streamer as streamer_ns
from .capture.controller import api as capture_ns
from .studio.controller import api as studio_ns
from .user.controller import api as user_ns

authorizations = {"apikey": {"type": "apiKey", "in": "header", "name": "X-API-KEY"}}

# Import controller APIs as namespaces.
api_bp = Blueprint("api", __name__)

api = Api(
    api_bp, title="API", description="Main routes.", authorizations=authorizations
)

# API namespaces
api.add_namespace(user_ns)
api.add_namespace(studio_ns)
api.add_namespace(camera_ns)
api.add_namespace(streamer_ns)
api.add_namespace(manufacturer_ns)
api.add_namespace(capture_ns)
