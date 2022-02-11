from flask_restx import Namespace, fields


class CameraDto:

    api = Namespace("camera", description="Camera related operations.")
    camera = api.model(
        "Camera Object",
        {
            "id": fields.String,
            "name": fields.String,
            "utm_x": fields.Float,
            "utm_y": fields.Float,
            "owner_id": fields.Integer,
            "manufacturer_id": fields.String,
            "resolution_x": fields.Integer,
            "resolution_y": fields.Integer,
            "url": fields.Url,
            "connection_date": fields.DateTime,
            "status": fields.Integer,
            "created_at": fields.DateTime,
            "updated_at": fields.DateTime,
        },
    )

    camera_resp = api.model(
        "Camera Data Response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "camera": fields.Nested(camera),
        },
    )

    camera_manufacturer = api.model(
        "Camera Manufacturer Object",
        {
            "id": fields.String,
            "name": fields.String,
        },
    )

    manufacturer_resp = api.model(
        "Camera Manufacturer Response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "manufacturer": fields.Nested(camera_manufacturer),
        },
    )
