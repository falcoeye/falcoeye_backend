from flask import Blueprint
from flask_restx import Api

from .controller import api as auth_ns

# Import auth namespace

auth_bp = Blueprint("auth", __name__)

auth = Api(
    auth_bp, title="G-Authenticate", description="Authenticate and receive tokens."
)

# API namespaces
auth.add_namespace(auth_ns)
