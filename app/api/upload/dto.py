from flask_restx import Namespace, fields


class UploadDto:
    api = Namespace("upload", description="Upload related operations.")

    upload_registry_key = api.model(
        "Upload registry key",
        {
            "upload_status": fields.String,
            "status": fields.Boolean,
            "message": fields.String,
            "registry_key": fields.String,
        },
    )
