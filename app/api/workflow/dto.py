from flask_restx import Namespace, fields


class WorkflowDto:
    api = Namespace("workflow", description="Workflow related operations.")

    workflow_post_data = api.model(
        "Workflow post data",
        {
            "name": fields.String,
            "aimodel_id": fields.String,
            "usedfor": fields.String,
            "consideration": fields.String,
            "assumption": fields.String,
            "thumbnail_url": fields.String,
            "structure_file": fields.String,
        },
    )

    workflow_short = api.model(
        "Camera list item",
        {
            "id": fields.String,
            "name": fields.String,
            "creator": fields.String,
            "publish_date": fields.DateTime,
        },
    )

    workflow_list = api.model(
        "Workflow list",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "workflow": fields.List(fields.Nested(workflow_short)),
        },
    )

    workflow = api.model(
        "Workflow Object",
        {
            "name": fields.String,
            "creator": fields.String,
            "publish_date": fields.DateTime,
            "aimodel_id": fields.String,
            "usedfor": fields.String,
            "consideration": fields.String,
            "assumption": fields.String,
            "thumbnail_url": fields.String,
            "structure_file": fields.String,
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
