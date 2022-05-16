from flask_restx import Namespace, fields


class AnalysisDto:
    api = Namespace("analysis", description="Analysis related operations.")
    analysis = api.model(
        "Analysis Object",
        {
            "name": fields.String,
            "creation_date": fields.DateTime,
            "workflow_id": fields.String,
            "status": fields.String,
            "results_path": fields.String,
        },
    )

    analysis_resp = api.model(
        "Analysis Data Response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "analysis": fields.Nested(analysis),
        },
    )
