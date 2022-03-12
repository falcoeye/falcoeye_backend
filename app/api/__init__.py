from flask import Blueprint, current_app
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_restx import Api

from .aimodel.controller import api as aimodel_ns
from .analysis.controller import api as analysis_ns
from .camera.controller import api_camera as camera_ns
from .camera.controller import api_manufacturer as manufacturer_ns
from .camera.controller import api_streamer as streamer_ns
from .capture.controller import api as capture_ns
from .dataset.controller import api as dataset_ns
from .studio.controller import api as studio_ns
from .user.controller import api as user_ns
from .workflow.controller import api as workflow_ns

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
api.add_namespace(manufacturer_ns)
api.add_namespace(workflow_ns)
api.add_namespace(dataset_ns)
api.add_namespace(aimodel_ns)
api.add_namespace(analysis_ns)
# api.add_namespace(aimodel_ns)
# api.add_namespace(analysis_ns)


@api.errorhandler(NoAuthorizationError)
def handle_not_authorized_exception(error):
    current_app.logger.error(error)
    return {"message": "not authorized"}, 401
