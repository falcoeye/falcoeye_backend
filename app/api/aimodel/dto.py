from flask_restx import Namespace, fields


class AIModelDto:
    api = Namespace("aimodel", description="AIModel related operations.")
    aimodel = api.model(
        "AIModel Object",
        {
            "name": fields.String,
            "publish_date": fields.DateTime,
            "archeticture": fields.String,
            "backbone": fields.String,
            "dataset_id": fields.String,
            "technology": fields.String,
            "speed": fields.String,
            "created_at": fields.DateTime,
            "updated_at": fields.DateTime,
        },
    )

    aimodel_resp = api.model(
        "AIModel Data Response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "aimodel": fields.Nested(aimodel),
        },
    )
