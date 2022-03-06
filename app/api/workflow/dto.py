from flask_restx import Namespace, fields


class WorkflowDto:
    api = Namespace("workflow", description="Workflow related operations.")
    workflow = api.model(
        "Worflow Object",
        {
            "name": fields.String,
            # "creator": fields.Integer,
            "publish_date": fields.DateTime,
            "aimodel_id": fields.String,
            "usedfor": fields.String,
            "consideration": fields.String,
            "assumption": fields.String,
            "accepted_media": fields.String,
            "results_type": fields.String,
            "thumbnail_url": fields.String,
            "created_at": fields.DateTime,
            "updated_at": fields.DateTime,
        },
    )

    workflow_resp = api.model(
        "Workflow Data Response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "workflow": fields.Nested(workflow),
        },
    )
