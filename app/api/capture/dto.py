from flask_restx import Namespace, fields


class CaptureDto:
    api = Namespace("capture", description="Capture related operations.")

    capture_post_data = api.model(
        "Capture post data",
        {
            "camera_id": fields.String,
            "capture_type": fields.String,
            "length": fields.Integer,
        },
    )

    capture_registry_key = api.model(
        "Capture registry key",
        {
            "capture_status": fields.String,
            "status": fields.Boolean,
            "message": fields.String,
            "registry_key": fields.String,
            "temporary_path": fields.String,
        },
    )

    capture_registry_post = api.model(
        "Capture data",
        {"status": fields.String, "message": fields.String},
    )

    capture_data = api.model(
        "Capture data",
        {
            "registry_key": fields.String,
            "capture_status": fields.String,
            "message": fields.String,
            "capture_path": fields.String,
        },
    )
