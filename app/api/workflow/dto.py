from flask_restx import Namespace, fields


class WorkflowDto:
    api = Namespace("workflow", description="Workflow related operations.")

    workflow_post_data = api.model(
        "Workflow post data",
        {
            "name": fields.String,
            "usedfor": fields.String,
            "consideration": fields.String,
            "assumption": fields.String,
            "results_description": fields.String,
            "structure": fields.Raw,
            "base64_img": fields.String,
        },
    )

    workflow_params = api.model(
        "Workflow params",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "workflow_params": fields.Raw,
        },
    )

    workflow_short = api.model(
        "Workflow list item",
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
            "aimodel_name": fields.String,
            "usedfor": fields.String,
            "consideration": fields.String,
            "assumption": fields.String,
        },
    )

    workflow_resp = api.model(
        "Workflow Data Response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "workflow": fields.Nested(workflow),
            "lastPage": fields.Boolean,
        },
    )
    workflow_count_resp = api.model(
        "Workflow Data Count Response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "workflow_count": fields.Integer,
        },
    )
