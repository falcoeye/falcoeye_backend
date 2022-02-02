from flask_restx import fields
from flask_restx import Namespace


class UserDto:
    

    api = Namespace(
        "user",
        description="User related operations."
    )
    user = api.model(
        "User object",
        {
            "email": fields.String,
            "name": fields.String,
            "username": fields.String,
            "joined_date": fields.DateTime,
            "role_id": fields.Integer
        }
    )

    data_resp = api.model(
        "User Data Response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "user": fields.Nested(user)
        }
    )
