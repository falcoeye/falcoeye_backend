from flask_restx import Namespace, fields


class AnalysisDto:
    api = Namespace("analysis", description="Analysis related operations.")
    analysis = api.model(
        "Analysis Object",
        {
            "id": fields.String,
            "name": fields.String,
            "creator": fields.String,
            "created_at": fields.DateTime,
            "workflow_id": fields.String,
            "status": fields.String,
            "results_path": fields.String,
        },
    )

    analysis_post = api.model(
        "Analysis post data",
        {
            "name": fields.String,
            "workflow_id": fields.String,
            "workflow_params": fields.Arbitrary,
        },
    )

    analysis_short = api.model(
        "Analysis short",
        {
            "id": fields.String,
            "name": fields.String,
            "created_at": fields.DateTime,
            "workflow_id": fields.String,
            "status": fields.String,
        },
    )

    analysis_list = api.model(
        "Analysis list",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "analysis": fields.List(fields.Nested(analysis_short)),
            "lastPage": fields.Boolean,
        },
    )

    analysis_resp = api.model(
        "Analysis Data Response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "analysis": fields.Nested(analysis),
            "lastPage": fields.Boolean,
        },
    )
